"""Recetas de reparación para cada diagnóstico de setup.

Cada `SetupRemedy` está indexada por el `check.id` que produce
`common.progress.setup_diagnostics`. El dashboard y el CLI consumen
estas recetas para mostrar una instrucción corta + el comando exacto
(Windows / macOS / Linux) solo cuando un check falla o emite aviso.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class FixCommand:
    label: str
    command: str


@dataclass(frozen=True)
class SetupRemedy:
    instruction: str
    commands: tuple[FixCommand, ...] = field(default_factory=tuple)
    note: str | None = None
    docs_url: str | None = None
    docs_label: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


_REMEDIES: dict[str, SetupRemedy] = {
    "python_version": SetupRemedy(
        instruction="Instala Python 3.12 o superior y reinicia la terminal.",
        docs_url="https://www.python.org/downloads/",
        docs_label="python.org/downloads",
    ),
    "uv_available": SetupRemedy(
        instruction="Instala `uv` y reabre esta terminal:",
        commands=(
            FixCommand(
                "Windows (PowerShell)",
                'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"',
            ),
            FixCommand(
                "macOS / Linux",
                "curl -LsSf https://astral.sh/uv/install.sh | sh",
            ),
        ),
        note="Si lo instalaste hace un momento, basta con cerrar y abrir la terminal.",
    ),
    "dependencies": SetupRemedy(
        instruction="Sincroniza las dependencias del proyecto:",
        commands=(FixCommand("Cualquier OS", "uv sync"),),
    ),
    "env_file": SetupRemedy(
        instruction="Copia la plantilla a `.env`:",
        commands=(
            FixCommand("Windows (PowerShell)", "Copy-Item .env.example .env"),
            FixCommand("macOS / Linux", "cp .env.example .env"),
        ),
    ),
    "api_key_present": SetupRemedy(
        instruction=(
            "Obtén una clave en Google AI Studio y añade "
            "`GEMINI_API_KEY=AIza...` dentro de `.env`."
        ),
        docs_url="https://aistudio.google.com/app/apikey",
        docs_label="aistudio.google.com/app/apikey",
    ),
    "api_key_valid": SetupRemedy(
        instruction="Lanza un ping real contra Gemini:",
        commands=(FixCommand("Cualquier OS", "arkanum doctor"),),
    ),
    "database": SetupRemedy(
        instruction="Registra al aprendiz:",
        commands=(FixCommand("Cualquier OS", "arkanum init"),),
    ),
    "dashboard": SetupRemedy(
        instruction="Arranca el dashboard:",
        commands=(FixCommand("Cualquier OS", "arkanum dashboard start"),),
    ),
    "workspace": SetupRemedy(
        instruction=(
            "La carpeta viene incluida en el repo. Si la borraste, recréala "
            "en la raíz:"
        ),
        commands=(
            FixCommand(
                "Windows (PowerShell)",
                "New-Item -ItemType Directory workspace | Out-Null",
            ),
            FixCommand("macOS / Linux", "mkdir -p workspace"),
        ),
        note="Sandbox del agente a partir del Acto II (Quest 05+).",
    ),
}


def remedy_for(check_id: str) -> SetupRemedy | None:
    return _REMEDIES.get(check_id)
