# AI Agent Quest

<p align="center">
    <img src="./assets/images/ai-quest-banner.png" alt="AI Agent Quest Banner" width="100%">
</p>

> *“Bienvenidos, aprendices.*
>
> *Durante años, muchos han confundido a los agentes con magia.*
>
> *Creen que nacen de prompts grandiosos o frameworks complejos.*
>
> *Pero la verdad es más simple… y más peligrosa.*
>
> *Un agente es voluntad.*
>
> *La capacidad de percibir, razonar y actuar sobre el mundo.*
>
> *En este laboratorio no aprenderán únicamente a utilizar herramientas.*
>
> *Aprenderán a comprenderlas.*
>
> *Forjarán memoria donde antes había olvido.*
>
> *Conectarán herramientas donde antes solo existía lenguaje.*
>
> *Y, paso a paso, darán forma a sistemas capaces de actuar más allá de una simple conversación.*
>
> *Cada Quest representa un fragmento del conocimiento del Laboratorio Arkanum.*
>
> *Algunos de ustedes crearán simples ecos.*
>
> *Otros… se convertirán en Arquitectos de Agentes.”*
>
> — **Zhyréon**, Director del Laboratorio Arkanum

AI Agent Quest es una travesía práctica para aprender cómo funcionan realmente los agentes IA modernos.

A lo largo de cada Quest, los aprendices construirán agentes desde cero: aprenderán a otorgar memoria, conectar herramientas, consultar conocimiento, ejecutar workflows y comunicarse mediante protocolos modernos como MCP.

Aquí no buscamos únicamente usar frameworks.  

Buscamos comprender el mecanismo detrás de ellos.

---

## El Camino del Aprendiz

```text
Prompt → Memoria → Herramientas → Conocimiento → Protocolos → Sistemas
```

Cada Quest introduce:

- un concepto clave
- un laboratorio práctico
- un reto técnico
- una nueva habilidad para el agente

---

## Roadmap

- Quest 01 — Tu Primer Agente
- Quest 02 — Memoria y Contexto
- Quest 03 — Herramientas y Function Calling
- Quest 04 — El Directorio Prohibido
- Quest 05 — RAG y Bibliotecas de Conocimiento
- Quest 06 — Frameworks de Agentes
- Quest 07 — Workflows y Orquestación
- Quest 08 — Protocolos MCP
- Quest 09 — Sistemas Multi-Agente
- Quest Final — El Arquitecto de Agentes

---

## Filosofía del Laboratorio

Primero entendemos los fundamentos.  

Luego utilizamos frameworks.

Los agentes no son magia.  

Son sistemas.

---

## Requisitos previos

Antes de comenzar necesitarás:

- Python 3.12+
- Git
- uv

---

## Instalación de uv

`uv` es el gestor de paquetes y entornos utilizado por el laboratorio.
Nos permite instalar y ejecutar todas las dependencias de forma simple y reproducible.

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Verificar instalación

```bash
uv --version
```

Si todo salió correctamente, ya puedes continuar con la instalación del laboratorio.

---

## Inicio Rápido

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd ai-agent-quest
```

### 2. Instalar dependencias

```bash
uv sync
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Agrega tu API key:

```env
GEMINI_API_KEY=your_api_key
```

### 4. Iniciar el primer Quest

```bash
uv run python quests/quest_01_first_agent/starter/agent.py
```

---