"""Servicio de render de Markdown para el viewer de quests y el Códex.

Responsabilidades:
- Renderizar `.md` a HTML con `markdown-it-py`.
- Reescribir links relativos para que naveguen dentro del dashboard:
    * `../../docs/foo/bar.md`        -> `/codex/foo/bar`
    * `./foo/bar.md`                 -> `/codex/foo/bar`        (cuando origen está en docs/)
    * `../../assets/images/x.png`    -> `/assets/images/x.png`
    * `../quest_02_arcane_gauge/...` -> `/quest/quest_02_arcane_gauge`
- Resaltar bloques de código con Pygments.
- Extraer un TOC plano (H1..H3) para la columna lateral.

Los links absolutos (`http://`, `https://`, `mailto:`, anchors `#...`) se
preservan sin tocar. Tampoco se reescriben rutas que apunten a archivos
no soportados (ej. `.py`, `.json`).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DOCS_DIR = (_REPO_ROOT / "docs").resolve()
_QUESTS_DIR = (_REPO_ROOT / "quests").resolve()
_ASSETS_DIR = (_REPO_ROOT / "assets").resolve()

_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$", re.MULTILINE)
_SLUG_RE = re.compile(r"[^a-z0-9]+")
_HTML_HREF_RE = re.compile(r"(<a\b[^>]*?\bhref=)([\"'])(.*?)\2", re.IGNORECASE)
_HTML_SRC_RE = re.compile(r"(<img\b[^>]*?\bsrc=)([\"'])(.*?)\2", re.IGNORECASE)
_DOC_LINK_RE = re.compile(
    r"""<a\b([^>]*\bhref=["'](?:https?://[^"']*|/(?:codex|quest|assets)(?:/[^"']*)?)["'][^>]*)>""",
    re.IGNORECASE,
)
_HAS_TARGET_RE = re.compile(r"\btarget\s*=", re.IGNORECASE)
_HAS_REL_RE = re.compile(r"\brel\s*=", re.IGNORECASE)

_PYGMENTS_FORMATTER = HtmlFormatter(nowrap=False, cssclass="hl", style="monokai", noclasses=False)


@dataclass(frozen=True)
class TocEntry:
    level: int
    text: str
    anchor: str


@dataclass(frozen=True)
class RenderedMarkdown:
    html: str
    toc: tuple[TocEntry, ...]
    title: str | None


def _slugify(text: str) -> str:
    base = _SLUG_RE.sub("-", text.lower()).strip("-")
    return base or "section"


def _extract_toc(source: str) -> tuple[tuple[TocEntry, ...], str | None]:
    entries: list[TocEntry] = []
    seen: dict[str, int] = {}
    title: str | None = None
    for hashes, text in _HEADING_RE.findall(source):
        level = len(hashes)
        clean_text = text.strip().rstrip("#").strip()
        anchor = _slugify(clean_text)
        if anchor in seen:
            seen[anchor] += 1
            anchor = f"{anchor}-{seen[anchor]}"
        else:
            seen[anchor] = 0
        if level == 1 and title is None:
            title = clean_text
        entries.append(TocEntry(level=level, text=clean_text, anchor=anchor))
    return tuple(entries), title


def _highlight(code: str, lang: str | None) -> str:
    try:
        if lang:
            lexer = get_lexer_by_name(lang, stripall=False)
        else:
            lexer = guess_lexer(code)
    except (ClassNotFound, ValueError):
        return (
            "<pre class=\"codeblock\"><code>"
            + escape(code)
            + "</code></pre>"
        )
    highlighted = highlight(code, lexer, _PYGMENTS_FORMATTER)
    return f"<div class=\"codeblock\" data-lang=\"{escape(lang or '')}\">{highlighted}</div>"


def _is_external(url: str) -> bool:
    if not url:
        return True
    if url.startswith(("#", "mailto:", "tel:")):
        return True
    scheme = urlsplit(url).scheme
    return scheme in {"http", "https", "data", "ftp"}


def _rewrite_target(source_path: Path, raw_href: str) -> str | None:
    """Devuelve la URL reescrita, o None si no debe tocarse."""
    if _is_external(raw_href):
        return None

    parts = urlsplit(raw_href)
    target_rel = parts.path
    if not target_rel:
        return None

    try:
        target = (source_path.parent / target_rel).resolve()
    except (OSError, ValueError):
        return None

    suffix = target.suffix.lower()

    if _ASSETS_DIR in target.parents or target == _ASSETS_DIR:
        try:
            rel = target.relative_to(_ASSETS_DIR).as_posix()
        except ValueError:
            return None
        return _join_url(f"/assets/{rel}", parts.fragment)

    if suffix == ".md" and (_DOCS_DIR in target.parents or target == _DOCS_DIR):
        try:
            rel = target.relative_to(_DOCS_DIR).with_suffix("").as_posix()
        except ValueError:
            return None
        if rel.lower() == "readme":
            return _join_url("/codex", parts.fragment)
        return _join_url(f"/codex/{rel}", parts.fragment)

    if suffix == ".md" and _QUESTS_DIR in target.parents:
        try:
            rel = target.relative_to(_QUESTS_DIR).as_posix()
        except ValueError:
            return None
        slug = rel.split("/", 1)[0]
        if target.name.lower() == "readme.md":
            return _join_url(f"/quest/{slug}", parts.fragment)

    return None


def _join_url(path: str, fragment: str) -> str:
    if fragment:
        return urlunsplit(("", "", path, "", fragment))
    return path


def _rewrite_inline_html(source_path: Path, text: str) -> str:
    """Reescribe href/src en bloques de HTML crudo embebido en el .md."""
    def sub_attr(match: re.Match) -> str:
        prefix, quote, value = match.group(1), match.group(2), match.group(3)
        new_value = _rewrite_target(source_path, value)
        if new_value is None:
            return match.group(0)
        return f"{prefix}{quote}{new_value}{quote}"

    text = _HTML_HREF_RE.sub(sub_attr, text)
    text = _HTML_SRC_RE.sub(sub_attr, text)
    return text


def _build_renderer(source_path: Path) -> MarkdownIt:
    md = MarkdownIt("commonmark", {"html": True, "linkify": True, "typographer": False})
    md.enable(["table", "strikethrough"])

    default_fence = md.renderer.rules.get("fence")
    default_code_block = md.renderer.rules.get("code_block")

    def fence(tokens, idx, options, env):
        token = tokens[idx]
        return _highlight(token.content, (token.info or "").strip().split(" ")[0] or None)

    def code_block(tokens, idx, options, env):
        token = tokens[idx]
        return _highlight(token.content, None)

    md.renderer.rules["fence"] = fence
    md.renderer.rules["code_block"] = code_block

    default_link = md.renderer.rules.get("link_open")

    def _rewrite_attr(token, attr_name: str) -> None:
        href = token.attrGet(attr_name)
        if href is None:
            return
        new_href = _rewrite_target(source_path, href)
        if new_href is not None:
            token.attrSet(attr_name, new_href)

    def link_open(tokens, idx, options, env):
        _rewrite_attr(tokens[idx], "href")
        if default_link:
            return default_link(tokens, idx, options, env)
        return md.renderer.renderToken(tokens, idx, options, env)

    md.renderer.rules["link_open"] = link_open

    default_image = md.renderer.rules.get("image")

    def image(tokens, idx, options, env):
        _rewrite_attr(tokens[idx], "src")
        if default_image:
            return default_image(tokens, idx, options, env)
        return md.renderer.renderToken(tokens, idx, options, env)

    md.renderer.rules["image"] = image

    # Envolver cada tabla en un contenedor con scroll horizontal propio. En
    # pantallas estrechas una tabla ancha (p. ej. la de comandos del Códex)
    # desbordaría el viewport; el wrapper la deja hacer scroll sin empujar el
    # ancho de la página. No se toca el `<table>` en sí, así que en desktop
    # se sigue renderizando igual.
    default_table_open = md.renderer.rules.get("table_open")
    default_table_close = md.renderer.rules.get("table_close")

    def table_open(tokens, idx, options, env):
        if default_table_open:
            rendered = default_table_open(tokens, idx, options, env)
        else:
            rendered = md.renderer.renderToken(tokens, idx, options, env)
        return '<div class="table-wrap">' + rendered

    def table_close(tokens, idx, options, env):
        if default_table_close:
            rendered = default_table_close(tokens, idx, options, env)
        else:
            rendered = md.renderer.renderToken(tokens, idx, options, env)
        return rendered + "</div>"

    md.renderer.rules["table_open"] = table_open
    md.renderer.rules["table_close"] = table_close

    default_heading_open = md.renderer.rules.get("heading_open")
    counters: dict[str, int] = {}

    def heading_open(tokens, idx, options, env):
        token = tokens[idx]
        inline = tokens[idx + 1]
        text = inline.content.strip().rstrip("#").strip()
        anchor = _slugify(text)
        if anchor in counters:
            counters[anchor] += 1
            anchor = f"{anchor}-{counters[anchor]}"
        else:
            counters[anchor] = 0
        token.attrSet("id", anchor)
        if default_heading_open:
            return default_heading_open(tokens, idx, options, env)
        return md.renderer.renderToken(tokens, idx, options, env)

    md.renderer.rules["heading_open"] = heading_open

    # Asegurar que `_` para evitar warnings: usamos las defaults guardadas
    _ = default_fence, default_code_block

    return md


def _open_doc_links_in_new_tab(html: str) -> str:
    """Abre links a documentación en pestaña nueva.

    Cubre links del contenido renderizado: `/codex/...`, `/quest/...`,
    `/assets/...` y URLs externas (`http(s)://`). Mantiene la lectura del
    pergamino sin interrumpirla: el aprendiz puede dejar la referencia
    abierta en background o leerla en paralelo.

    Quedan intactos: anchors internos (`#section`), `mailto:`/`tel:`, y
    cualquier `<a>` que ya defina su propio `target`.
    """
    def add_target(match: re.Match) -> str:
        attrs = match.group(1)
        if _HAS_TARGET_RE.search(attrs):
            return match.group(0)
        addition = ' target="_blank"'
        if not _HAS_REL_RE.search(attrs):
            addition += ' rel="noopener noreferrer"'
        return f"<a{attrs}{addition}>"

    return _DOC_LINK_RE.sub(add_target, html)


def _render_markdown_text(text: str, source_path: Path) -> RenderedMarkdown:
    """Renderiza `text` como Markdown, reescribiendo enlaces relativos respecto
    a `source_path` (que puede ser un archivo virtual para contenido generado)."""
    toc, title = _extract_toc(text)
    text = _rewrite_inline_html(source_path, text)
    md = _build_renderer(source_path)
    html = md.render(text)
    html = _open_doc_links_in_new_tab(html)
    return RenderedMarkdown(html=html, toc=toc, title=title)


def render_markdown_file(source_path: Path) -> RenderedMarkdown:
    """Renderiza un archivo `.md`. Lanza FileNotFoundError si no existe."""
    return _render_markdown_text(source_path.read_text(encoding="utf-8"), source_path)


def pygments_css() -> str:
    """CSS para los temas de Pygments. Inyectable inline."""
    return _PYGMENTS_FORMATTER.get_style_defs(".hl")


def resolve_codex_path(rel_path: str) -> Path | None:
    """Resuelve `rel_path` dentro de `docs/`. Devuelve None si sale del árbol o no existe."""
    if not rel_path or rel_path.lower() == "readme":
        candidate = _DOCS_DIR / "README.md"
        return candidate if candidate.exists() else None

    safe = rel_path.strip("/").replace("\\", "/")
    if ".." in safe.split("/"):
        return None

    base = (_DOCS_DIR / safe).resolve()
    if _DOCS_DIR not in base.parents and base != _DOCS_DIR:
        return None

    if base.suffix == "":
        for candidate in (base.with_suffix(".md"), base / "README.md"):
            if candidate.exists() and candidate.is_file():
                return candidate
        return None

    if base.is_file() and base.suffix.lower() == ".md":
        return base
    return None


# Títulos legibles para las secciones (subcarpetas) del Códex. Si una carpeta
# no está aquí, se usa su nombre capitalizado como fallback.
_SECTION_TITLES = {
    "terminal": "Terminal",
    "cli": "CLI del laboratorio",
    "python": "Python",
    "LLMs": "Modelos de Lenguaje (LLMs)",
    "agents": "Agentes",
    "security": "Seguridad",
}


def resolve_codex_dir(rel_path: str) -> Path | None:
    """Devuelve el Path de un subdirectorio de `docs/` (para renderizar un
    índice de sección), o None si no es un directorio válido dentro de docs/."""
    if not rel_path:
        return None
    safe = rel_path.strip("/").replace("\\", "/")
    if ".." in safe.split("/"):
        return None
    base = (_DOCS_DIR / safe).resolve()
    if base == _DOCS_DIR or _DOCS_DIR not in base.parents:
        return None
    return base if base.is_dir() else None


def _doc_title(path: Path) -> str:
    """Título (primer H1) de un .md; si no tiene, el nombre legible del archivo."""
    try:
        _, title = _extract_toc(path.read_text(encoding="utf-8"))
    except OSError:
        title = None
    return title or path.stem.replace("_", " ").replace("-", " ")


def render_codex_section(dir_path: Path) -> RenderedMarkdown:
    """Genera y renderiza un índice de sección: lista las entradas (.md) del
    directorio con su título, ordenadas alfabéticamente. Auto-generado, sin
    necesidad de mantener un README por carpeta."""
    rel = dir_path.relative_to(_DOCS_DIR).as_posix()
    section_name = _SECTION_TITLES.get(rel, rel.replace("_", " ").title())
    entries = sorted(
        (
            p for p in dir_path.iterdir()
            if p.suffix.lower() == ".md" and p.name.lower() != "readme.md"
        ),
        key=lambda p: _doc_title(p).lower(),
    )
    lines = [f"# {section_name}", ""]
    if entries:
        lines.append(f"Entradas del Códex en esta sección ({len(entries)}):")
        lines.append("")
        for entry in entries:
            lines.append(f"- [{_doc_title(entry)}](./{entry.name})")
    else:
        lines.append("_Esta sección aún no tiene entradas._")
    text = "\n".join(lines) + "\n"
    # `source_path` virtual dentro del directorio: hace que `./x.md` se reescriba
    # a `/codex/<rel>/x` con la lógica de enlaces ya existente.
    return _render_markdown_text(text, dir_path / "index.md")


def resolve_quest_readme(slug: str) -> Path | None:
    """Devuelve la ruta al README de un quest, si existe."""
    base = (_QUESTS_DIR / slug).resolve()
    if _QUESTS_DIR not in base.parents:
        return None
    readme = base / "README.md"
    return readme if readme.exists() else None
