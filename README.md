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

<p align="center">
    <img src="./assets/images/ai-quest-roadmap-main-banner-image.png" alt="Roadmap del Curso" width="100%">
</p>


AI Agent Quest está dividido en 4 grandes actos.

Cada acto representa una nueva etapa en la evolución del agente:

desde una simple invocación hasta sistemas capaces de actuar, razonar y colaborar.

```text
Prompt → Memoria → Herramientas → Conocimiento → Protocolos → Sistemas
```

---

### ACTO I — Fundamentos del Agente

> *“Antes de construir inteligencia, debes comprender conversación, contexto y voluntad.”*
> — Zhyréon

En este acto aprenderás los fundamentos detrás de los modelos conversacionales modernos:

- prompts
- temperatura
- contexto
- roles
- instrucciones del sistema
- consumo de tokens
- debugging básico
- estructura de interacción con LLMs

Aquí construiremos la primera voz del agente.

### ACTO II — Capacidad de Acción

> *“Una voz inteligente puede responder preguntas.  
> Un agente encarnado puede transformar el mundo.”*  
> — Zhyréon

El aprendiz abandona la teoría.

En este acto construiremos los primeros componentes reales de un sistema agéntico:

- working directories
- guardrails
- tool schemas
- function calling
- function dispatch
- tool execution
- agent loops iterativos
- observaciones estructuradas
- verbose mode
- ciclos de razonamiento y manifestación

Al finalizar este acto, el agente podrá:

- explorar archivos
- leer contenido
- escribir programas
- ejecutar código
- observar resultados
- iterar sobre problemas
- corregir errores utilizando tools reales

### ACTO III — Inteligencia Extendida

> *“La memoria individual es limitada.*
> *Los grandes arquitectos construyen bibliotecas.”*
> — Zhyréon

Exploraremos recuperación de conocimiento, workflows y protocolos modernos para agentes.

⚠️ Este acto se encuentra en desarrollo.

### ACTO IV — Arquitectura de Agentes

> *“Cuando múltiples inteligencias cooperan, nace una arquitectura.”*
> — Zhyréon

Construiremos sistemas multi-agente, evaluación y proyectos finales.

⚠️ Este acto se encuentra en desarrollo.

---

Cada Quest introduce:

- un concepto clave
- un laboratorio práctico
- un reto técnico
- una nueva habilidad para el agente

---

## Filosofía del Laboratorio

Primero entendemos los fundamentos.  

Luego utilizamos frameworks.

Los agentes no son magia.  

Son sistemas.

---

<p align="center">
    <img src="./assets/images/arcane-codex-main-banner-image.png" alt="The Arcane Codex" width="100%">
</p>

El laboratorio incluye una biblioteca de referencia llamada:

```text
docs/
```

El Códex contiene explicaciones sobre:
- terminal
- Python
- LLMs
- agentes
- tokens
- memoria
- contexto conversacional

Puedes consultarlo en cualquier momento durante el laboratorio y usarlo para ampliar tus conocimientos o consultar cosas que te llamen la atención. Se incluyen referencias a las entradas relevantes en los README de cada quest.

```text
docs/README.md
```

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

### Verificar instalación

```bash
uv --version
```

Si todo salió correctamente, ya puedes continuar con la instalación del laboratorio.

> **Si `uv --version` falla justo después de instalarlo**, cierra y vuelve a abrir la terminal. El instalador deja `uv` en `%USERPROFILE%\.local\bin` (Windows) o `~/.local/bin` (macOS / Linux) y agrega esa ruta al `PATH` del usuario, pero las sesiones abiertas no recogen el cambio hasta reiniciarse.

---

## Inicio Rápido

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd AIAgentQuest
```

### 2. Instalar dependencias

```bash
uv sync
```

`uv sync` crea el entorno virtual en `.venv/` e instala el ejecutable del laboratorio en `.venv/Scripts/arkanum.exe` (Windows) o `.venv/bin/arkanum` (macOS / Linux), gracias a la entrada `[project.scripts]` declarada en `pyproject.toml`.

### 3. Activar el entorno (para tener `arkanum` en el PATH)

Para que el comando `arkanum` esté disponible directamente desde la terminal, activa el entorno virtual:

**Windows (PowerShell):**

```powershell
. .\.venv\Scripts\Activate.ps1
```

> Si PowerShell rechaza el script con un error de política de ejecución, ejecuta una sola vez:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

Verifica que el comando responde:

```bash
arkanum --help
```

Deberías ver los 10 subcomandos del laboratorio: `doctor`, `init`, `current`, `next`, `progress`, `start`, `run`, `check`, `cost`, `dashboard`.

> **Alternativa sin activar el venv.** Cada vez que abras una terminal nueva puedes invocar el CLI con `uv run arkanum ...` en lugar de activar el entorno. Por ejemplo: `uv run arkanum --help`.

### 4. Configurar variables de entorno

Crea un archivo `.env` a partir del ejemplo `.env.example`:

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

Edita `.env` y reemplaza el placeholder por tu clave real de Gemini (la obtienes gratis en [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) → *Create API key*):

```env
GEMINI_API_KEY=AIza...
```

> Sin comillas, sin espacios, una sola línea.

### 5. Registrar tu aprendiz y abrir el dashboard

Crea tu perfil local de progreso con el wizard del CLI:

```bash
arkanum init
```

El wizard te pedirá tu nombre, verificará tu `.env`, hará ping a Gemini y abrirá el **dashboard arcano** en tu navegador. Esto también crea la base SQLite local de tu progreso:

```text
.quest_progress.db
```

> El archivo es personal y no debe subirse a Git (ya está en `.gitignore`).

**Dashboard arcano** — disponible por defecto en [http://127.0.0.1:8765](http://127.0.0.1:8765). Ahí encontrarás:

- **Perfil** — tu rango, nivel, XP, pills de logros y panel de diagnóstico del setup.
- **Mapa** — los 4 actos y todas las quests con su estado (actual / completada / sellada).
- **Rangos / Hitos** — colección de rangos desbloqueados y actos cerrados.
- **Setup** — diagnóstico continuo de los 9 prerrequisitos; si algo falla muestra instrucciones puntuales para arreglarlo.
- **Live Agent** — visualización en vivo del agent loop (a partir del Acto II).

Atajos útiles del CLI:

```bash
arkanum progress           # tabla de tu avance
arkanum current            # quest en la que estás
arkanum doctor             # diagnóstico completo (incluye ping real a Gemini)
arkanum dashboard status   # PID y puerto del server
arkanum dashboard stop     # detenerlo
arkanum dashboard start    # volver a levantarlo
```

### 6. Comenzar el primer Quest

Cada Quest contiene:

- teoría breve
- objetivos
- instrucciones paso a paso
- starter code
- validaciones
- solución final

Para saber cuál es tu quest actual:

```bash
arkanum current
```

Esto te indicará, por ejemplo, **Quest 1 — La Primera Invocación**. Abre el README correspondiente:

```text
quests/quest_01_first_invocation/README.md
```

o desde terminal:

```bash
code quests/quest_01_first_invocation/README.md
```

Sigue las instrucciones del Quest y trabaja sobre:

```text
starter/main.py
```

Para ejecutar tu starter mientras avanzas:

```bash
arkanum start 1
```

Cuando termines, valida tu solución con:

```bash
arkanum check 1
```

Si la solución pasa, el dashboard sella la quest, otorga el rango correspondiente y abre la página de celebración automáticamente.

---

## Estructura del repositorio (lo esencial)

```text
AIAgentQuest/
├── quests/              # Una carpeta por quest (Q01–Q08)
│   └── quest_NN_*/
│       ├── README.md    # Teoría + instrucciones
│       ├── starter/     # Código que tú editas
│       ├── solution/    # Solución de referencia
│       └── workspace/   # Sandbox específico de la quest (Acto II+)
├── common/              # CLI, dashboard, progreso, funciones compartidas
├── docs/                # Códex arcano (referencia de conceptos)
├── workspace/           # Sandbox libre del agente para tus experimentos
├── .env                 # Tu API key (no se sube a git)
└── .quest_progress.db   # Tu progreso local (no se sube a git)
```

---

## Si algo no funciona

El laboratorio incluye dos herramientas de diagnóstico que te dicen exactamente qué arreglar:

### 1. Pestaña **Setup** del dashboard

Visita [http://127.0.0.1:8765/setup](http://127.0.0.1:8765/setup). Verás los 9 checks del laboratorio (Python, uv, dependencias, `.env`, API key, BD, dashboard, workspace) con su estado en tiempo real. Cuando algo falla, aparece debajo una sección **"Cómo arreglar"** con el comando exacto para Windows y macOS / Linux. El panel se refresca solo cada 30 segundos.

### 2. Comando `arkanum doctor`

```bash
arkanum doctor
```

Misma información en la terminal, en formato tabla, y con un ping real a Gemini para verificar que tu clave funciona.

### Problemas comunes

- **`arkanum` no se encuentra** → no activaste el venv. Vuelve al paso 3 o usa `uv run arkanum ...`.
- **`uv` no se encuentra después de instalarlo** → cierra y vuelve a abrir la terminal (el `PATH` del usuario se actualiza, pero las sesiones abiertas no lo recogen).
- **El dashboard no responde** → `arkanum dashboard status` para ver si está vivo; si no, `arkanum dashboard start`.
- **API key inválida** → revisa que la clave en `.env` no tenga comillas, espacios ni saltos de línea, y que siga activa en [aistudio.google.com](https://aistudio.google.com).

---

## Opcional: Experiencia visual arcana en VSCode

Este curso fue diseñado con una pequeña capa estética inspirada en un laboratorio arcano, solo por diversión y ambientación ✨

Para una mejor experiencia visual, se recomienda utilizar VSCode e instalar:

- [Material Icon Theme](https://marketplace.visualstudio.com/items?itemName=PKief.material-icon-theme)

El repositorio ya incluye un archivo de configuración de VSCode con asociaciones de íconos personalizadas para las quests y carpetas del laboratorio.

Una vez instalado el plugin, la ambientación visual debería aplicarse automáticamente al abrir el proyecto. 

Esto es completamente opcional, pero ayuda a que la academia se sienta un poco más viva ✨
