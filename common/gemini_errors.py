"""Clasificación de errores de Gemini en categorías accionables.

La capa gratuita de Gemini tiene rate limits agresivos y cuota diaria baja, así
que estos errores son comunes en un laboratorio educativo. Sin clasificarlos,
un 429 se ve como un traceback crudo del SDK o —peor— como "API key inválida",
desalentando al aprendiz cuando su clave está perfectamente bien.

Es **defensivo**: no depende de los tipos exactos del SDK `google-genai` (que
cambian entre versiones). Mira el `code`/`status` si el error lo expone y, como
respaldo, el texto del error. Por eso clasifica tanto excepciones como strings
(el wrapper `arkanum start` solo tiene el mensaje del stdout, no la excepción).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

GeminiErrorKind = Literal["quota", "auth", "server", "network", "unknown"]


@dataclass(frozen=True)
class GeminiError:
    kind: GeminiErrorKind
    title: str  # encabezado corto, en lenguaje llano
    hint: str   # qué puede hacer el aprendiz


# Pistas de texto por categoría (se buscan en minúsculas). Defensivo ante las
# variaciones de mensaje del SDK y de la API REST/gRPC.
_QUOTA_HINTS = (
    "resource_exhausted", "quota", "rate limit", "ratelimit", "rate-limit",
    "too many requests", "exceeded your current quota", "exhausted",
)
_AUTH_HINTS = (
    "api key not valid", "api_key_invalid", "invalid api key", "api key expired",
    "permission_denied", "permission denied", "unauthenticated", "unauthorized",
)
_SERVER_HINTS = (
    "internal error", "internal server", "unavailable", "overloaded",
    "backend error", "deadline_exceeded", "service is currently",
)
_NETWORK_HINTS = (
    "connection", "timed out", "timeout", "temporary failure", "name resolution",
    "getaddrinfo", "ssl", "max retries", "connection refused", "connection reset",
    "failed to establish",
)


def classify_gemini_error(error: object) -> GeminiError:
    """Clasifica una excepción (o su texto) de Gemini en una categoría útil."""
    code = _status_code(error)
    text = _error_text(error).lower()

    if code == 429 or _matches(text, _QUOTA_HINTS):
        return GeminiError(
            "quota",
            "Límite de Gemini alcanzado (cuota o rate limit)",
            "Tu clave es válida; la capa gratuita tiene un tope por minuto y por "
            "día. Espera ~1 minuto y reintenta, o revisa tu cuota en "
            "https://aistudio.google.com/.",
        )
    if code in (401, 403) or _matches(text, _AUTH_HINTS):
        return GeminiError(
            "auth",
            "La API key de Gemini no es válida o no tiene permisos",
            "Revisa GEMINI_API_KEY en tu archivo .env. Si hace falta, genera una "
            "nueva en https://aistudio.google.com/app/apikey.",
        )
    if (code is not None and 500 <= code < 600) or _matches(text, _SERVER_HINTS):
        return GeminiError(
            "server",
            "Gemini tuvo un problema temporal del servidor",
            "No es tu código ni tu clave. Reintenta en unos momentos.",
        )
    if _matches(text, _NETWORK_HINTS):
        return GeminiError(
            "network",
            "No se pudo conectar con Gemini",
            "Revisa tu conexión a internet (o un proxy/firewall) y reintenta.",
        )
    return GeminiError(
        "unknown",
        "Error al llamar a Gemini",
        "Revisa el mensaje completo. Si persiste, vuelve a intentar en un rato.",
    )


def _status_code(error: object) -> int | None:
    """Código HTTP del error si el SDK lo expone (`code` / `status_code`)."""
    for attr in ("code", "status_code"):
        val = getattr(error, attr, None)
        if isinstance(val, bool):
            continue
        if isinstance(val, int):
            return val
        if isinstance(val, str) and val.isdigit():
            return int(val)
    return None


def _error_text(error: object) -> str:
    """Texto representativo del error, juntando str() y atributos comunes."""
    if isinstance(error, str):
        return error
    parts = [type(error).__name__, str(error)]
    for attr in ("message", "status", "reason"):
        val = getattr(error, attr, None)
        if isinstance(val, str):
            parts.append(val)
    return " ".join(parts)


def _matches(text: str, hints: tuple[str, ...]) -> bool:
    return any(hint in text for hint in hints)
