# El Códex Arcano

<p align="center">
    <img src="../assets/images/arcane-codex-illustration-banner.png" alt="The Arcane Codex" width="100%">
</p>

> “Los Quests enseñan el camino.
> El Códex preserva la sabiduría.”
>
> — Zhyréon

No todo conocimiento pertenece a un Quest.

Algunas verdades son demasiado antiguas, demasiado profundas o demasiado peligrosas para enseñarse durante una simple invocación.

Por eso existe este códice.

Aquí descansan fragmentos del conocimiento del Laboratorio Arkanum:
- principios sobre agentes
- notas sobre modelos de lenguaje
- estructuras conversacionales
- herramientas del laboratorio
- fundamentos de terminal y Python
- observaciones sobre memoria, contexto y razonamiento

Los Quests enseñan a construir.
El Códice a comprender.

---

# Índice del Códex

> ¿Por dónde empezar? Si eres nuevo, lee en este orden: **Terminal y CLI → Python → Modelos de Lenguaje (LLMs) → Agentes → Seguridad**.

## Terminal y CLI

Fundamentos para navegar la terminal y usar el CLI del laboratorio (`arkanum *`).

- [cli basics](./terminal/cli-basics.md)
- [help flags](./terminal/flags.md)
- [`--verbose` mode](./terminal/verbose_mode.md)
- [comandos del CLI (`arkanum *`)](./cli/commands.md)

---

## Python

Herramientas y conceptos del lenguaje utilizados durante el laboratorio.

- [`argparse`](./python/argparse.md)
- [función `main` / `__main__`](./python/main_function.md)
- [variables de entorno](./python/environment_variables.md)

---

## Modelos de Lenguaje (LLMs)

Los fundamentos sobre los que se construye todo agente. Si empiezas, lee esta sección primero.

- [¿qué es un LLM?](./LLMs/llms.md)
- [tokens](./LLMs/tokens.md)
- [roles y mensajes](./LLMs/roles_and_messages.md)
- [prompts de sistema](./LLMs/system_prompts.md)
- [temperatura](./LLMs/temperature.md)

---

## Agentes

Cómo un LLM se convierte en un agente que percibe, razona y actúa con herramientas.

- [¿qué es un agente?](./agents/agents.md)
- [`Content` y `Parts`](./agents/content_and_parts.md)
- [definir herramientas (schemas)](./agents/tool_schemas.md)
- [despacho de funciones](./agents/function_dispatch.md)
- [manejo de errores](./agents/error_handling.md)
- [guardrails](./agents/guardrails.md)

---

## Seguridad

Cómo confinar al agente para que actúe solo dentro de su territorio permitido.

- [validación de rutas](./security/path_validation.md)

---

## Interno (mantenedores)

Documentación de infraestructura del propio laboratorio. No es necesaria para resolver las quests.

- [tracing — emitir al Live Agent](./agents/tracing.md)

---

> *“Toda conversación deja un eco.*
>
> *Toda herramienta deja una marca.*
>
> *Y todo arquitecto deja conocimiento para quienes caminan después.”*