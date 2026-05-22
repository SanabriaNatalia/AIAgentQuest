"""Helpers ligeros para inspeccionar archivos fuente sin ejecutarlos.

Los pre-checks usan dos estrategias complementarias:

1. **Regex sobre texto raw** (`regex_in_source`) — útil para detectar strings
   literales o patrones que viven dentro de comentarios/docstrings (p. ej.
   "Prompt tokens:" que se imprime con f-string).
2. **AST estático** (`parse_source`, `has_import`, `has_call`,
   `has_attribute_access`, `has_function_def`) — más robusto que regex para
   imports, llamadas y definiciones.

Todos los helpers tratan `SyntaxError` y "archivo no existe" como condiciones
de falla controlada: las funciones devuelven `False` y los call sites
deciden cómo reportarlo.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path


def read_source(path: Path) -> str | None:
    """Lee el archivo como UTF-8. Devuelve None si no existe."""
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def parse_source(path: Path) -> ast.AST | None:
    """Parsea el archivo a AST. Devuelve None si no existe o tiene SyntaxError."""
    source = read_source(path)
    if source is None:
        return None
    try:
        return ast.parse(source, filename=str(path))
    except SyntaxError:
        return None


def regex_in_source(path: Path, pattern: str, flags: int = 0) -> bool:
    source = read_source(path)
    if source is None:
        return False
    return re.search(pattern, source, flags) is not None


def has_import(tree: ast.AST, module: str, name: str | None = None) -> bool:
    """¿El AST contiene `import module` o `from module import name`?

    Si `name` es None, basta con que el módulo esté importado.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == module or alias.name.startswith(module + "."):
                    if name is None:
                        return True
        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue
            if node.module == module or node.module.startswith(module + "."):
                if name is None:
                    return True
                for alias in node.names:
                    if alias.name == name:
                        return True
    return False


def has_call(tree: ast.AST, qualified_name: str) -> bool:
    """¿El AST contiene una llamada cuyo callable matchea `qualified_name`?

    Acepta:
    - "ArgumentParser" → ast.Name("ArgumentParser")
    - "load_dotenv"    → ast.Name("load_dotenv")
    - "genai.Client"   → ast.Attribute(value=Name("genai"), attr="Client")
    - "client.models.generate_content" → cadena anidada de Attribute
    """
    parts = qualified_name.split(".")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _matches_dotted(node.func, parts):
            return True
    return False


def has_attribute_access(tree: ast.AST, qualified_name: str) -> bool:
    """¿El AST contiene un acceso a atributo qualified_name (sin requerir llamada)?

    Ejemplo: `response.usage_metadata` → busca un Attribute(attr="usage_metadata")
    cuyo value sea un Name("response"). Acepta también cadenas más largas como
    `result.parts[0].function_response`.
    """
    parts = qualified_name.split(".")
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and _matches_dotted(node, parts):
            return True
    return False


def has_function_def(tree: ast.AST, name: str) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return True
    return False


def has_for_range(tree: ast.AST, range_arg_name: str | None = None) -> bool:
    """¿Hay un `for _ in range(...)` (opcionalmente con un arg específico)?"""
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            iter_node = node.iter
            if (
                isinstance(iter_node, ast.Call)
                and isinstance(iter_node.func, ast.Name)
                and iter_node.func.id == "range"
            ):
                if range_arg_name is None:
                    return True
                for arg in iter_node.args:
                    if isinstance(arg, ast.Name) and arg.id == range_arg_name:
                        return True
    return False


def call_has_kwarg(tree: ast.AST, qualified_name: str, kwarg: str) -> bool:
    """¿Existe una llamada `qualified_name(...)` con keyword `kwarg=...`?"""
    parts = qualified_name.split(".")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _matches_dotted(node.func, parts):
            for kw in node.keywords:
                if kw.arg == kwarg:
                    return True
    return False


def _matches_dotted(node: ast.AST, parts: list[str]) -> bool:
    """¿La cadena de Attribute/Name reproduce exactamente `parts`?"""
    current: ast.AST = node
    for piece in reversed(parts):
        if isinstance(current, ast.Attribute):
            if current.attr != piece:
                return False
            current = current.value
        elif isinstance(current, ast.Name):
            if current.id != piece:
                return False
            return True
        else:
            return False
    return False
