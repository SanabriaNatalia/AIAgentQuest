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

AI Agent Quest está dividido en 4 grandes actos.

Cada acto representa una nueva etapa en la evolución del agente:

desde una simple invocación hasta sistemas capaces de actuar, razonar y colaborar.

---

# ACTO I — Fundamentos del Agente

> *“Antes de construir inteligencia, debes comprender conversación, contexto y memoria.”*
> — Zhyréon

En este acto aprenderás los fundamentos detrás de los agentes modernos:

- prompts
- contexto
- memoria
- roles
- instrucciones del sistema
- consumo de tokens

Aquí construiremos el núcleo conversacional del agente.

# ACTO II — Capacidad de Acción

> *“Una voz inteligente es útil.*
> *Un agente capaz de actuar cambia el mundo.”*
> — Zhyréon

El agente aprenderá a utilizar herramientas y operar sobre el mundo exterior.

⚠️ Este acto se encuentra en desarrollo.

---

# ACTO III — Inteligencia Extendida

> *“La memoria individual es limitada.*
> *Los grandes arquitectos construyen bibliotecas.”*
> — Zhyréon

Exploraremos recuperación de conocimiento, workflows y protocolos modernos para agentes.

⚠️ Este acto se encuentra en desarrollo.

---

# ACTO IV — Arquitectura de Agentes

> *“Cuando múltiples inteligencias cooperan, nace una arquitectura.”*
> — Zhyréon

Construiremos sistemas multi-agente, evaluación y proyectos finales.

⚠️ Este acto se encuentra en desarrollo.

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

Crea un archivo `.env` a partir del ejemplo `.env.example` 
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