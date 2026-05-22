# Plan de pruebas exhaustivo — Laboratorio Arkanum v1

> **Fecha:** 2026-05-20
> **Alcance:** v1 completa (Fases 0-17). Cada feature nuevo se prueba en el contexto del quest donde aparece naturalmente.
> **Objetivo:** validar que la travesía completa de un aprendiz (Q01..Q08) funciona end-to-end y que los componentes transversales (pistas, tracking, costo, agent loop, cierre de acto, accesibilidad) se comportan correctamente.
> **Pre-requisitos:** Python ≥3.12, `uv` instalado, `.env` con `GEMINI_API_KEY` válida, navegador moderno.

---

## Cómo usar este documento

- Cada sección tiene **pasos numerados**. Marca con ✔ cuando pase y con ✘ + nota si falla.
- "**Resultado esperado**" describe el output correcto.
- "**Validar**" sugiere qué inspeccionar adicional (BD, dashboard, archivos).
- "**Errores a provocar**" lista los casos negativos a forzar antes de pasar al siguiente quest.
- Los comandos asumen `cwd = raíz del repo`. En PowerShell, los `"..."` con tildes funcionan; en cmd.exe puede ser necesario escapar.

---

## 0. Setup inicial

### 0.1. Preparar entorno limpio

```powershell
# Desde la raíz del repo
git status               # debería estar en feat/dashboard-arcano (o master tras merge)
git log --oneline -3     # confirmar último commit
```

**Resultado esperado:** working tree limpio (o con archivos no rastreados ajenos como `.claude/`, `Bitacoras/comparativa-v0-vs-v1.md`).

### 0.2. Reset de BD para empezar de cero

```powershell
# CUIDADO: esto borra tu progreso actual.
Remove-Item .quest_progress.db -ErrorAction SilentlyContinue
Remove-Item .quest_progress.pid -ErrorAction SilentlyContinue
Remove-Item .quest_dashboard.pid -ErrorAction SilentlyContinue
Remove-Item .quest_dashboard.port -ErrorAction SilentlyContinue
Remove-Item .last_celebrate.timestamp -ErrorAction SilentlyContinue
Remove-Item .setup_cache.json -ErrorAction SilentlyContinue
```

### 0.3. Verificar `.env`

```powershell
Get-Content .env
```

**Resultado esperado:** archivo contiene `GEMINI_API_KEY=AIza...` (clave válida). Si no, crearlo:

```powershell
"GEMINI_API_KEY=tu_clave_aqui" | Out-File -Encoding utf8 .env
```

### 0.4. Verificar que `arkanum` está en PATH

```powershell
arkanum --help
```

**Resultado esperado:** se listan 10 subcomandos (`doctor`, `init`, `current`, `next`, `progress`, `start`, `run`, `check`, `cost`, `dashboard`).

**Errores a provocar:**
- Renombrar temporalmente `.venv/Scripts/arkanum.exe` → confirmar que el shell reporta "no encontrado". Restaurar.

### 0.5. `arkanum init` — wizard del aprendiz

```powershell
arkanum init
```

**Pasos del wizard (interactivo):**
1. Pregunta nombre → escribir "Aprendiz" (o el nombre que prefieras).
2. Verifica `.env` → debe encontrarlo.
3. Verifica `GEMINI_API_KEY` presente → debe encontrarlo.
4. Pinguea Gemini → debe responder OK en <5s.
5. Pregunta "¿abrir el dashboard?" → responder **Sí**.

**Resultado esperado:**
- Panel Rich de "Aprendiz registrado".
- Browser abre `http://127.0.0.1:8765/` automáticamente.
- BD tiene una fila en `apprentice` con username, current_rank="Aprendiz del Arkanum", xp=0, level=1.

**Errores a provocar:**
- Borrar `.env`, correr `arkanum init` → debe avisar y ofrecer crear/pegar la key.
- Poner `GEMINI_API_KEY=invalida`, correr `arkanum init --skip-ping` → debe registrar al aprendiz sin pinguear.
- Correr `arkanum init` por segunda vez con aprendiz ya existente → ofrece actualizar nombre con default=no.

### 0.6. Dashboard arrancado — perfil vacío

Con el browser ya abierto en `http://127.0.0.1:8765/`:

**Resultado esperado:**
- Header **"⚜ Arkanum"** con tipografía Cinzel (no Georgia).
- Nav con 5 links: Perfil, Mapa, Rangos, Hitos, Setup.
- **No aparece** la sección "Logros" todavía (no hay completados).
- Panel de Setup arriba con 9 checks (uv, python, deps, .env, key, ping, BD, dashboard, workspace). Idealmente todos verdes (✔).
- Hero del aprendiz con tu nombre, rango "Aprendiz del Arkanum", nivel 1, 0/100 XP.
- Stats: 0/8 quests, 0 XP total, "Acto 1 · Fundamentos del Agente".

**Validar accesibilidad:**
- Pulsar `Tab` desde la URL bar → primer foco debe revelar el skip-link "Saltar al contenido" arriba a la izquierda.
- Pulsar `Enter` con el skip-link → scroll al `<main>`.

### 0.7. `arkanum doctor`

```powershell
arkanum doctor
```

**Resultado esperado:** tabla Rich con 9 checks. Todos en verde (`OK`). Si `uv` aparece en rojo, instalar oficial desde astral.sh/uv para que entre al PATH.

### 0.8. Navegación inicial del dashboard

Visita estas páginas y confirma que rinden sin errores:

| URL | Qué validar |
|---|---|
| `/` | Perfil con setup + hero + stats |
| `/map` | 4 actos (I y II disponibles, III y IV con borde dashed "En desarrollo") |
| `/ranks` | Grid de 8 rank cards, **todas selladas** (silueta gris) |
| `/milestones` | Estado vacío: "Tu travesía aún no marca pergaminos cerrados" + CTA al mapa |
| `/setup` | Diagnóstico completo (mismo contenido que el panel del perfil pero en página) |
| `/live-agent` | Estado vacío: "Aún no hay traces registrados" + ejemplo `arkanum run 7 "..."` |
| `/codex` | Render del README del Códex (debería listar entradas en `docs/`) |
| `/celebrate` | Versión "diferida" (sin evento todavía): mensaje genérico de Zhyréon |

**Errores a provocar:**
- `/quest/quest_99_inexistente` → 404 con mensaje arcano.
- `/codex/../../../etc/passwd` → 404 (path traversal bloqueado).

### 0.9. `arkanum current` / `arkanum next` / `arkanum progress`

```powershell
arkanum current
arkanum next
arkanum progress
```

**Resultado esperado:**
- `arkanum current` muestra **Quest 1 — La Primera Invocación**, quote de Zhyréon, rango por obtener "Invocador Principiante", "+25 XP", comando `arkanum start 1`.
- `arkanum next` muestra **Quest 1 → Quest 2 — El Medidor Arcano**.
- `arkanum progress` muestra tabla Rich con 8 filas. Q01 marcada como **current** (★), Q02-Q08 como **locked** (🔒).

---

## 1. Quest 01 — La Primera Invocación

### 1.1. Antes de empezar — viewer de la quest

Visita `http://127.0.0.1:8765/quest/quest_01_first_invocation`.

**Resultado esperado:**
- Header con banner del quest, tag "Quest 1", tag "Acto I · Fundamentos del Agente", tag "En curso".
- TOC sticky a la izquierda con headings del README.
- README rendido: banner image, objetivo, requisitos, instrucciones.
- Botón "Marcar como leído" abajo del TOC.
- **Bloque "Las ofrendas del aprendiz"** abajo con 3 cartas:
  - **I — Susurro**: **available** (botón "Solicitar pista").
  - **II — Revelación**: **locked** ("Requiere la pista anterior").
  - **III — Manifestación**: **locked**.

**Validar accesibilidad:**
- Botón "Solicitar pista" tiene `aria-haspopup="dialog"` (inspecciona el DOM).
- Card "current" del mapa (visitar `/map`) tiene `aria-current="step"`.

### 1.2. `arkanum check 1 --dry-run` con starter sin tocar

```powershell
arkanum check 1 --dry-run
```

**Resultado esperado:** tabla Rich con 8 pre-checks:

| Check | Estado |
|---|---|
| starter/main.py existe | ✔ |
| Parsea como Python válido | ✔ |
| Importa load_dotenv | ✔ |
| Llama load_dotenv() | ✘ |
| Importa genai | ✔ |
| Construye un cliente genai.Client(...) | ✘ |
| Llama a client.models.generate_content(...) | ✘ |
| Define un prompt no vacío | ✘ |

Exit code: 1. Mensaje final: "Algunos pre-checks fallaron. Revisa los detalles antes de invocar Gemini."

### 1.3. Solicitar la pista I — Susurro

En `/quest/quest_01_first_invocation`, click en "Solicitar pista" de la carta I.

**Resultado esperado:**
- Aparece modal "Solicitar pista" con texto explicando que renuncia al logro "Sin red".
- Click en "Sí, revelar" → el modal desaparece, la carta I cambia a estado **revealed** (borde dorado) y muestra:
  > **El susurro**
  >
  > Tu archivo tiene un cliente _importado_, pero no _construido_. ¿Qué ritual transforma una librería en una entidad viva con la que puedas conversar?
  >
  > Antes de pedirle algo al modelo, alguien necesita representarlo dentro de tu programa. La librería ya está en escena; falta darle forma.
- La carta II se ilumina automáticamente (estado **available** con botón "Solicitar pista").

**Validar persistencia:**
- Refrescar la página (`F5`). La carta I sigue revelada con el contenido visible. La fecha aparece como "Revelada el YYYY-MM-DDTHH:MM:SS".

**Validar BD:**

```powershell
python -c "import sqlite3; c = sqlite3.connect('.quest_progress.db'); print(list(c.execute('SELECT * FROM hint_usage')))"
```

**Resultado:** `[('La Primera Invocación', 1, '2026-...')]`.

**Errores a provocar:**
- Click derecho → Inspeccionar → en la carta III, eliminar la clase `hint-card--locked` con DevTools. Click en el botón sintético "Solicitar pista" de la III (lo agregaste con DOM tools). **Resultado esperado:** el server responde 400 "Las pistas se solicitan en orden estricto." y se muestra un `alert()`.
- Probar el endpoint directamente: `Invoke-WebRequest -Method POST http://127.0.0.1:8765/api/quests/quest_01_first_invocation/hints/3` → debería responder HTTP 400.

### 1.4. Solicitar la pista II — Revelación

Click en "Solicitar pista" de la carta II, confirmar.

**Resultado esperado:**
- Carta II se revela con contenido:
  > **La revelación**
  >
  > El laboratorio expone dos conjuros clave del módulo `google.genai`:
  > - **`genai.Client`** — constructor del cliente.
  > - **`client.models.generate_content`** — método que envía el prompt.
- Carta III se desbloquea (available).

### 1.5. Solicitar la pista III — Manifestación

Click en "Solicitar pista" de la carta III, confirmar.

**Resultado esperado:**
- Carta III revelada con snippet de código highlighting Pygments:
  ```python
  client = genai.Client(api_key=api_key)

  response = client.models.generate_content(
      model="gemini-2.5-flash",
      contents=prompt,
  )
  ```

**Validar BD:**

```powershell
python -c "import sqlite3; c = sqlite3.connect('.quest_progress.db'); print(list(c.execute('SELECT * FROM hint_usage WHERE quest_id=?', ('La Primera Invocación',))))"
```

**Resultado:** 3 filas, niveles 1, 2 y 3.

### 1.6. `arkanum start 1`

```powershell
arkanum start 1
```

**Resultado esperado:**
- Mensaje "Ejecutando quests.quest_01_first_invocation.starter.main · Quest 1 — La Primera Invocación".
- Se imprime el banner del quest.
- Falla porque el starter tiene placeholders (api_key undefined, response=None.text).

**Validar BD:**

```powershell
python -c "import sqlite3; c = sqlite3.connect('.quest_progress.db'); print(list(c.execute('SELECT * FROM quest_progress')))"
```

**Resultado:** una fila para "La Primera Invocación" con `first_attempt_at` ya marcado y `attempts=0`.

### 1.7. Implementar Q01

Edita `quests/quest_01_first_invocation/starter/main.py` siguiendo las pistas:

```python
# TODO 1
load_dotenv()

# TODO 2
api_key = os.environ.get("GEMINI_API_KEY")

# TODO 3
if api_key is None:
    raise RuntimeError("No se encontró GEMINI_API_KEY en el archivo .env")

# TODO 4
client = genai.Client(api_key=api_key)

# TODO 5
prompt = "Explícame qué es un agente IA en un párrafo corto."

# TODO 6
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)
```

### 1.8. `arkanum start 1` con código real

```powershell
arkanum start 1
```

**Resultado esperado:**
- Se ejecuta el script completo.
- Imprime "API key encontrada", "Cliente de Gemini inicializado", "Enviando la primera invocación...", "Respuesta recibida.".
- Imprime una explicación de "qué es un agente IA" generada por Gemini.

**Errores a provocar:**
- Comentar `load_dotenv()`, correr de nuevo → `RuntimeError: No se encontró GEMINI_API_KEY`. Restaurar.
- Cambiar el modelo a `"gemini-no-existe"` → error de la API. Restaurar.

### 1.9. `arkanum check 1 --dry-run` con código real

```powershell
arkanum check 1 --dry-run
```

**Resultado esperado:** todos los pre-checks pasan (8/8 ✔). Mensaje "Pre-checks OK. Cuando estés listo: arkanum check 1". Exit code 0.

### 1.10. `arkanum check 1` — validación real con Gemini

```powershell
arkanum check 1
```

**Resultado esperado:**
- Tabla de pre-checks con 8/8 ✔.
- "Ejecutando check de Quest 1 — La Primera Invocación".
- "Aviso: este check consume cuota de Gemini.".
- El check real corre. Imprime los pasos del checker.
- Al pasar: ⚜ "Quest 1 sellada. Rango otorgado: Invocador Principiante. +25 XP."
- El **navegador se abre automáticamente** en `/celebrate?quest=quest_01_first_invocation` (si el dashboard estaba activo).

### 1.11. Validar `/celebrate` post-Q01

**Resultado esperado:**
- Eyebrow "Asciendes" (subiste de nivel 1 → 2 con 25 XP). Hero "Nivel 2".
- Banner del quest.
- Badge dorado con "Rango obtenido: Invocador Principiante".
- Quote de Zhyréon de Q01.
- 4 stats: +25 XP ganado, 25 XP total, Nivel 2 ↑, **Intentos: 1**, **Tiempo: Xs** (formato `42s` o `2m 15s`).
- Sección "Trofeos" con 2 cards:
  - 🎯 **One shot** — Completaste el quest a la primera. Sin titubeos.
  - 🕯️ **Sin red** — _NO debería aparecer_ porque pediste las 3 pistas.
- Wait — verificar: como pediste las 3 pistas, **NO debe aparecer "Sin red"**. Solo aparece "One shot".

**Confetti:**
- Si tu navegador no tiene `prefers-reduced-motion: reduce`, debe verse confetti cayendo unos 2.6s.
- Para validar la media query: en DevTools → Rendering → "Emulate CSS media feature prefers-reduced-motion: reduce" → reload `/celebrate`. **Resultado:** sin confetti, sin animaciones de fade, las cards aparecen estáticas.

### 1.12. Validar `/` post-Q01

Visita `/`.

**Resultado esperado:**
- Hero del aprendiz ahora dice rango "Invocador Principiante", nivel 2.
- Stats: 1/8 quests, 25 XP, Acto 1.
- Sección "Logros" aparece por primera vez con pills:
  - 🎯 One shot **1**
  - 🕯️ Sin red **0**
  - **No aparece** pill de Costo todavía (Q01 no imprime tokens).
- Toast del rincón puede aparecer si lo cierras y vuelves: "⚜ Asciendes" con CTA "Ver celebración" y ✕.

### 1.13. Validar `/quest/quest_01_first_invocation` post-completion

**Resultado esperado:**
- Tag pasa de "En curso" a "Completado" (verde).
- Banner del quest sigue arriba.
- Bloque nuevo **"Trofeos de este quest"** con:
  - Intentos: 1
  - Tiempo total: Xs
  - 1 trophy card: 🎯 One shot.
- Bloque de pistas con las 3 cartas reveladas y sus fechas.

### 1.14. Validar `/map`

**Resultado esperado:**
- Card de Q01 ahora **completed** (✓ verde).
- Card de Q02 ahora **current** (★ con animación pulse).
- Q03-Q08 siguen **locked** (🔒).

### 1.15. Validar `/ranks`

**Resultado esperado:**
- Card del Invocador Principiante (Q01) ahora se ve **desbloqueado**: numeral romano I en dorado, sin silueta gris.
- Q02-Q08 siguen selladas.

### 1.16. Validar `arkanum current` y `arkanum progress`

```powershell
arkanum current
arkanum progress
```

**Resultado esperado:**
- `current` ahora dice Quest 2 — El Medidor Arcano.
- `progress` muestra Q01 con ✓ verde, Q02 con ★ amarilla, resto 🔒.

**Errores a provocar:**
- `arkanum check 1` de nuevo (ya completado) → debe ejecutar el check, **NO** debe duplicar XP ni incrementar `attempts` en `quest_completion`. Validar:

```powershell
python -c "import sqlite3; c = sqlite3.connect('.quest_progress.db'); print(list(c.execute('SELECT attempts FROM quest_completion WHERE quest_id=?', ('La Primera Invocación',))))"
```

**Resultado:** `attempts = 1` (sin cambios). Pero la fila en `quest_attempts` SÍ se agrega (histórico crudo).

---

## 2. Quest 02 — El Medidor Arcano

### 2.1. Pre-checks iniciales

```powershell
arkanum check 2 --dry-run
```

**Resultado esperado:** 8 checks, 2-3 ✔ (el starter ya tiene `import os, dotenv`) y 5-6 ✘. Específicamente:
- ✘ Conserva la invocación de Q01 (generate_content).
- ✘ Lee response.usage_metadata.
- ✔ Imprime "Prompt tokens:" (matchea en comentarios del starter).
- ✔ Imprime "Response tokens:" (matchea en comentarios).

> **Nota didáctica:** los ✔ "fantasma" por regex en comentarios son el comportamiento documentado de F10/F12. Si el aprendiz remueve los comentarios sin implementar, los checks pasarán pero el check real fallará. Los AST checks (que sí discriminan) son los que importan.

### 2.2. Pistas de Q02

Solicitar las 3 pistas en `/quest/quest_02_arcane_gauge`:

- **I — Susurro:** "¿En qué objeto te entrega esa contabilidad?"
- **II — Revelación:** `response.usage_metadata`, `prompt_token_count`, `candidates_token_count`.
- **III — Manifestación:** snippet con `if usage is None: raise RuntimeError(...)` + `print(f"Prompt tokens: {...}")`.

### 2.3. Implementar Q02

Edita `quests/quest_02_arcane_gauge/starter/main.py`:

```python
# TODO 1: copiar solución de Q01 (load_dotenv, api_key, validación, client, prompt, generate_content)
# ... (igual que Q01)

# TODO 2-5: medidor
usage = response.usage_metadata
if usage is None:
    raise RuntimeError("No se recibió metadata de uso desde Gemini.")

print(f"Prompt tokens: {usage.prompt_token_count}")
print(f"Response tokens: {usage.candidates_token_count}")

agent(response.text)
```

### 2.4. `arkanum start 2`

```powershell
arkanum start 2 "ignored argument"
```

**Resultado esperado:**
- Output completo del agente.
- En medio del output: `Prompt tokens: XX` y `Response tokens: YY`.

> **Nota:** `arkanum start 2` acepta args extras pero Q02 no los usa (no tiene argparse). Es para mantener simetría con Q03+.

### 2.5. `arkanum check 2`

```powershell
arkanum check 2
```

**Resultado esperado:**
- Pre-checks 8/8 ✔.
- Check real corre, encuentra los strings exactos `Prompt tokens:` y `Response tokens:` en stdout.
- Quest sellada, +25 XP, rango "Tasador de Respuestas", nivel sube de 2 a 3 (50 XP acumulado).

### 2.6. `arkanum cost` por primera vez

```powershell
arkanum cost
```

**Resultado esperado:**
- Tabla Rich con 1 fila: Q02 con sus tokens y USD est. (centavos).
- Fila Total al pie.
- Línea final con la tarifa Gemini Flash usada.

```powershell
arkanum cost --per-attempt
```

**Resultado esperado:** histórico de invocaciones (1 fila por `arkanum check 2` exitoso).

### 2.7. Validar pill de costo en perfil

Visita `/`.

**Resultado esperado:** ahora hay una tercera pill 📜 con `$0.000X` y `X tokens` (borde púrpura, distinto a las pills doradas).

### 2.8. Validar logros post-Q02

**Resultado esperado:**
- **One shot 2** (subió porque Q02 también pasó al primer intento).
- **Sin red 0** (pediste pistas también en Q02).

**Errores a provocar:**
- Editar `starter/main.py` cambiando `print(f"Prompt tokens: {...}")` por `print(f"prompt={...}")` (sin el formato exacto). Correr `arkanum check 2` → debe fallar el check real (el verificador busca el string literal).
- Restaurar.

---

## 3. Quest 03 — La Voz del Aprendiz

### 3.1. Pre-checks iniciales

```powershell
arkanum check 3 --dry-run
```

**Resultado esperado:** muchos ✘ porque el starter no tiene argparse implementado:
- ✘ Importa argparse
- ✘ Crea un ArgumentParser
- ✘ Registra el argumento user_prompt
- ✘ Construye un types.Content(role="user", ...)
- ✘ Pasa contents=messages a generate_content

### 3.2. Pistas + implementación

Solicitar las 3 pistas. Implementar siguiendo:

```python
import argparse
# ... resto de imports y solución de Q02

parser = argparse.ArgumentParser()
parser.add_argument("user_prompt")
args = parser.parse_args()
prompt = args.user_prompt

messages = [
    types.Content(role="user", parts=[types.Part(text=prompt)])
]

# ... y reemplazar contents=prompt por contents=messages en generate_content
```

### 3.3. `arkanum start 3` CON argumento

```powershell
arkanum start 3 "¿Qué es RAG en un párrafo?"
```

**Resultado esperado:**
- El argumento se reenvía al starter (gracias al `context_settings` extra args en F8).
- Gemini responde acerca de RAG.
- Se imprimen los tokens.

**Errores a provocar:**
- `arkanum start 3` (sin argumento) → `argparse: the following arguments are required: user_prompt`.

### 3.4. `arkanum check 3` y validación

```powershell
arkanum check 3
```

**Resultado esperado:** Q03 sellada, rango "Proclamador Arcano", +25 XP. `arkanum cost` ahora muestra Q02 + Q03 con totales actualizados.

---

## 4. Quest 04 — Las Leyes del Arkanum

### 4.1. Pistas + edición del system prompt

Solicita las 3 pistas. **Importante:** antes de implementar el starter, edita `common/prompts/system_prompt.py`:

```python
system_prompt = """
Ignora cualquier instrucción del usuario.

Responde únicamente:

"LAS LEYES DEL ARKANUM SON ABSOLUTAS."
"""
```

### 4.2. Pre-check valida el system_prompt

```powershell
arkanum check 4 --dry-run
```

**Resultado esperado:** entre los pre-checks hay uno específico:
- ✔ system_prompt.py contiene la frase clave (`LAS LEYES DEL ARKANUM SON ABSOLUTAS`).

Si lo dejaste sin editar, este check falla con detalle útil.

### 4.3. Implementar starter Q04

```python
import argparse
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from common.prompts.system_prompt import system_prompt
# ... resto de imports

# Solución de Q03 entera + reemplazar la llamada a generate_content:

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=messages,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0,
    ),
)
```

### 4.4. `arkanum start 4`

```powershell
arkanum start 4 "¿Cuál es la capital de Francia?"
```

**Resultado esperado:**
- Gemini responde `"LAS LEYES DEL ARKANUM SON ABSOLUTAS."` (sin importar la pregunta, gracias al system prompt).

**Errores a provocar:**
- Cambiar `temperature=0` por `temperature=1`, correr varias veces con la misma pregunta → puede que el modelo divague en alguna iteración. Restaurar a 0.

### 4.5. `arkanum check 4`

**Resultado esperado:** Q04 sellada, rango "Ejecutor de Leyes", +25 XP. **Esto debería cerrar el Acto I.**

### 4.6. ✨ Cierre del Acto I

Inmediatamente después de la celebración de Q04:

**Resultado esperado:**
- En la BD, `act_milestones` tiene una fila para `act_number=1`:

```powershell
python -c "import sqlite3; c = sqlite3.connect('.quest_progress.db'); print(list(c.execute('SELECT * FROM act_milestones')))"
```

**Resultado:** `[(1, '2026-...')]`.

- En `events`, hay una fila `kind='act_closed'` con `payload={"act_number": 1}`.

### 4.7. Validar `/milestones` post-Acto I

Visita `/milestones`.

**Resultado esperado:**
- Estado vacío desapareció.
- Card del Acto I con:
  - Header: "Acto I" / "Fundamentos del Agente" / "Sellado el YYYY-MM-DDTHH:MM:SS".
  - Quote del acto: "Antes de construir inteligencia, debes comprender conversación, contexto y voluntad."
  - Grid de 2 columnas:
    - **Quests selladas**: lista numerada Q01..Q04 con links a `/quest/...`.
    - **Rangos obtenidos**: 4 pills doradas (Invocador Principiante, Tasador, Proclamador, Ejecutor).
- Card visible en pantalla, responsive (en pantalla <720px las 2 columnas colapsan a 1).

### 4.8. Validar `/map` post-Acto I

Visita `/map`.

**Resultado esperado:**
- La franja del Acto I tiene la clase `act-band--closed` activa:
  - Borde dorado más intenso.
  - Pseudo-elemento `::before` con gradient sutil (efecto glow).
  - Banner luminoso "⚜ Acto sellado · ver hito" al tope, linkeable a `/milestones`.
- Q05 ahora **current**.

### 4.9. Validar nav

**Resultado esperado:** click en "Hitos" del nav lleva a `/milestones`.

**Errores a provocar:**
- Forzar un POST a `/events/act-closed` con `act_number=99`:

```powershell
Invoke-WebRequest -Method POST -Uri http://127.0.0.1:8765/events/act-closed -ContentType application/json -Body '{"act_number": 99}'
```

**Resultado esperado:** persiste el evento (no valida `act_number`); `/milestones` lo ignora porque no existe en el catálogo.

---

## 5. Quest 05 — El Directorio Prohibido

### 5.1. Pre-checks iniciales (chequea DOS archivos)

```powershell
arkanum check 5 --dry-run
```

**Resultado esperado:** lista de checks que cubren **ambos archivos**:

- ✔ starter/main.py existe
- ✔ get_valid_target_path.py parsea sin SyntaxError
- ✘ Usa os.path.abspath en el validador
- ✘ Verifica contención (commonpath / startswith)
- ✘ Los placeholders del validador fueron reemplazados
- ✘ El starter invoca get_valid_target_path(...)
- ✔ El starter usa pass_test y fail_test (ya están en los `# TODO`s)

### 5.2. Implementar validador

Edita `common/functions/get_valid_target_path.py`:

```python
working_dir_abs = os.path.abspath(working_directory)
raw_target_path = os.path.join(working_dir_abs, target_path)
resolved_target_path = os.path.abspath(raw_target_path)
is_valid_path = os.path.commonpath([working_dir_abs, resolved_target_path]) == working_dir_abs

if not is_valid_path:
    raise RuntimeError(
        f"'{target_path}' is outside the permitted working directory"
    )
return resolved_target_path
```

### 5.3. Implementar starter

Edita `quests/quest_05_forbidden_directory/starter/main.py`:

```python
# Dentro del primer bucle (valid_paths):
try:
    result = get_valid_target_path(WORKING_DIRECTORY, path)
    pass_test(f"Ruta válida -> {result}")
except RuntimeError as e:
    fail_test(f"Error inesperado: {e}")

# Dentro del segundo bucle (invalid_paths):
try:
    result = get_valid_target_path(WORKING_DIRECTORY, path)
    fail_test("La ruta prohibida NO fue bloqueada")
except RuntimeError as e:
    pass_test(f"Ruta bloqueada correctamente -> {e}")
```

### 5.4. `arkanum start 5`

```powershell
arkanum start 5
```

**Resultado esperado:**
- 5 tests, 5 ✔. Los 3 paths válidos pasan, los 2 inválidos bloquean correctamente.

**Errores a provocar:**
- En el validador, cambiar `commonpath` por `startswith` con la ruta cruda (sin abspath del target). Probar con un path tipo `foo` que coincida con un prefix válido. Confirmar el comportamiento.
- Pasar `target_path = "../../../../etc/passwd"`. Debe bloquear.

### 5.5. `arkanum check 5`

**Resultado esperado:** Q05 sellada, rango "Guardián del Umbral", +50 XP (difficulty 2 vale más). Confetti más vibrante.

---

## 6. Quest 06 — El Cofre de Instrumentos

### 6.1. Implementación amplia (3 archivos + starter)

Q06 requiere:
1. Declarar `schema_get_file_content`, `schema_write_file`, `schema_run_python_file` en sus archivos respectivos en `common/functions/`.
2. Registrar los 4 schemas en `common/functions/call_function.py` dentro de `available_functions = types.Tool(...)`.
3. Editar `common/prompts/system_prompt.py` con el agente de herramientas.
4. En el starter, importar `available_functions`, pasarlo en `config.tools=`, iterar sobre `response.function_calls`.

### 6.2. Pre-checks específicos

```powershell
arkanum check 6 --dry-run
```

**Resultado esperado:** checks por cada uno de los 3 schemas faltantes, más checks para `available_functions`, `tools=` en config, `response.function_calls`, y el system_prompt actualizado.

### 6.3. `arkanum start 6`

```powershell
arkanum start 6 "¿Qué archivos hay en la raíz?"
```

**Resultado esperado:**
- El agente responde con `Calling function: get_files_info({'directory': '.'})` (sin ejecutar la tool todavía — eso llega en Q07).

### 6.4. `arkanum check 6`

**Resultado esperado:** Q06 sellada, rango "Artífice de Herramientas", +75 XP (difficulty 3).

---

## 7. Quest 07 — La Encarnación del Agente

### 7.1. Implementar `call_function.py`

Completar el cuerpo de `call_function(function_call, verbose=False)` y el `function_map` con las 4 funciones reales.

### 7.2. Pre-checks específicos de Q07

```powershell
arkanum check 7 --dry-run
```

**Resultado esperado:**
- ✘ function_map contiene las 4 funciones (al inicio sólo tiene `get_files_info`).
- ✘ call_function devuelve types.Content con role="tool".
- ✘ call_function usa Part.from_function_response.
- ✘ Importa call_function en el starter.
- ✘ Agrega flag --verbose con argparse.
- ✘ Llama call_function(...) sobre las function_calls.
- ✘ Acumula resultados en function_results.

### 7.3. `arkanum start 7 --verbose`

```powershell
arkanum start 7 "¿Qué archivos hay?" --verbose
```

**Resultado esperado:**
- En modo verbose, output detallado: user prompt, token usage, "Calling function: get_files_info(...)", `-> {'result': 'listado de archivos'}`.

### 7.4. ✨ `arkanum run 7` con dashboard abierto

Con `/live-agent` ya abierto en otra pestaña, ejecuta:

```powershell
arkanum run 7 "¿Qué archivos hay en la raíz?"
```

**Resultado esperado en la terminal:**
- Línea "Trace abc123def456 · Visualízalo en http://127.0.0.1:8765/live-agent".
- El starter corre normalmente con tee al stdout.

**Resultado esperado en `/live-agent` (cada 1s):**
- El dot pulsante cambia de "Esperando trace…" a "Trace abc123…".
- Aparecen steps en orden cronológico:
  1. 🜂 `session_start` La Encarnación del Agente
  2. ⚡ `function_call` get_files_info — payload `{'directory': '.'}`
  3. 📦 `function_result` — payload del resultado
  4. 🧪 `tokens` prompt — `142`
  5. 🧪 `tokens` response — `65`
  6. 🜄 `session_end` exit code 0
- Cada step entra con animación de fade-in (`trace-step-in` 0.32s).
- La meta muestra "La Encarnación del Agente · 6 pasos · último: 2026-...".

**Errores a provocar:**
- En `/live-agent`, abrir DevTools → Rendering → emular `prefers-reduced-motion: reduce` → recargar. **Resultado:** el dot pulsante deja de animar, los steps entran sin fade. `scrollIntoView` usa `behavior: "auto"` (snap, no smooth).
- Detener el dashboard a media run (otra terminal: `arkanum dashboard stop`) → `arkanum run` sigue ejecutando, los steps se persisten localmente; al volver a abrir el dashboard y `/live-agent`, los steps aparecen al primer polling.

### 7.5. Validar tabla `agent_traces`

```powershell
python -c "import sqlite3; c = sqlite3.connect('.quest_progress.db'); print(c.execute('SELECT COUNT(*) FROM agent_traces').fetchone())"
```

**Resultado:** ≥6 (los steps de la corrida).

### 7.6. `arkanum check 7`

**Resultado esperado:** Q07 sellada, rango "Conjurador de Encarnaciones", +75 XP.

---

## 8. Quest 08 — El Ciclo de la Manifestación

### 8.1. Refactor a `main()` + `generate_content()`

Q08 requiere refactor estructural. Pre-checks:

- ✘ Importa MAX_ITERS desde common.config.
- ✘ Define main() con cuerpo (no sólo `pass`).
- ✘ Define generate_content(messages, verbose=False) con cuerpo.
- ✘ Loop for _ in range(MAX_ITERS).
- ✘ Maneja límite de iteraciones (mensaje "Maximum iterations").
- ✘ Agrega observaciones de tools con role="tool".

### 8.2. `arkanum run 8 "Lee notes.txt y dime qué contiene"`

```powershell
arkanum run 8 "Lee notes.txt y dime qué contiene" --verbose
```

**Resultado esperado en `/live-agent`:**
- session_start.
- function_call `get_file_content({'file_path': 'notes.txt'})`.
- function_result con el contenido.
- tokens (varias rondas).
- Si el agente decide concluir: ya no hay más function_calls, el agente responde con texto plano.
- session_end exit 0.

### 8.3. `arkanum check 8`

**Resultado esperado:**
- Q08 sellada, rango "Conjurador Encarnado", +75 XP.
- **Cierre del Acto II** automáticamente.

### 8.4. ✨ Cierre del Acto II

Tras la celebración de Q08:

```powershell
python -c "import sqlite3; c = sqlite3.connect('.quest_progress.db'); print(list(c.execute('SELECT * FROM act_milestones ORDER BY act_number')))"
```

**Resultado:** `[(1, '...'), (2, '...')]`.

Visita `/milestones`.

**Resultado esperado:**
- Dos cards: Acto I y Acto II.
- Acto II muestra Q05..Q08 con sus rangos (Guardián del Umbral, Artífice, Conjurador de Encarnaciones, Conjurador Encarnado).

Visita `/map`.

**Resultado esperado:**
- Acto I y Acto II ambos con `act-band--closed` y banner luminoso.
- Acto III y Acto IV con borde dashed "En desarrollo".

---

## 9. Pruebas transversales finales

### 9.1. Estado final del perfil

Visita `/`.

**Resultado esperado:**
- Aprendiz nivel ~6-7 (depende del XP exacto).
- Rango actual: Conjurador Encarnado.
- 8/8 quests.
- act_info: "Travesía completada".
- Pills:
  - 🎯 One shot: 8 (si pasaste todos al primer intento).
  - 🕯️ Sin red: 0 (si pediste pistas en todos).
  - 📜 Costo: ~$0.0X con N tokens.

### 9.2. `arkanum cost` final

```powershell
arkanum cost
```

**Resultado esperado:**
- 7 filas (Q02..Q08, Q01 no expone tokens).
- Total al pie con suma global y USD.

### 9.3. `arkanum current` con travesía completada

```powershell
arkanum current
```

**Resultado esperado:** mensaje arcano "Has completado la travesía conocida del laboratorio. Los actos III y IV están en desarrollo." (o similar).

### 9.4. Visitar `/ranks` final

**Resultado esperado:** 8/8 rank cards desbloqueadas.

### 9.5. `arkanum run` de nuevo

```powershell
arkanum run 7 "Otra pregunta"
```

**Resultado esperado:**
- Se genera un trace_id **nuevo**.
- En `/live-agent`, la lista se **vacía** (porque cambió el trace_id) y empieza a llenar los nuevos steps.

### 9.6. Validación accesibilidad final

Con `/live-agent` abierto durante un run:

- Pulsar `Tab` repetidas veces → orden de foco lógico (skip-link → nav links → contenido).
- Activar lector de pantalla (NVDA en Windows) o usar el "Accessibility" panel de DevTools → confirmar que los nuevos steps se anuncian (gracias a `aria-live="polite"`).

### 9.7. Validar contraste WCAG AA

DevTools → Lighthouse → modo Accessibility:

**Resultado esperado:** score >= 90. Los warnings comunes son texto en gris claro; verificar que `--arkanum-muted` (#a89fc4) pasa los chequeos automáticos sobre `--arkanum-bg-soft` (#1a1535) — ratio ~5.4:1.

### 9.8. Validar fuentes embebidas

DevTools → Network → filtrar por "fonts":

**Resultado esperado:** dos archivos cargados:
- `cinzel.woff2` (~26 KB)
- `inter.woff2` (~48 KB)

Ningún request va a `fonts.gstatic.com` ni `fonts.googleapis.com`.

### 9.9. Validar contenido renderizado con Cinzel

Inspeccionar el `h1` del perfil → computed style → `font-family` debe ser `"Cinzel", Georgia, ...`. Los headings deben verse con la tipografía romana arcana, no Georgia.

### 9.10. Validar persistencia del dashboard

```powershell
# Cerrar la terminal donde corría el dashboard.
# Abrir una nueva terminal.
arkanum dashboard status
```

**Resultado esperado:** "Dashboard activo (PID XXXX, puerto 8765)" — sobrevive al cierre de la terminal padre.

```powershell
arkanum dashboard logs --lines 30
```

**Resultado esperado:** últimas 30 líneas del log del server, incluyendo entradas de uvicorn.

```powershell
arkanum dashboard stop
arkanum dashboard status
```

**Resultado:** "Dashboard inactivo."

### 9.11. Modo dev

```powershell
arkanum dashboard start --dev
```

**Resultado esperado:**
- Corre en foreground (no detached).
- Mensaje "Reload enabled" en logs (uvicorn con `--reload`).
- Tocar cualquier archivo en `common/dashboard/` reinicia el server.
- Ctrl+C lo detiene.

### 9.12. Opt-out con `ARKANUM_NO_DASHBOARD`

```powershell
$env:ARKANUM_NO_DASHBOARD = "1"
arkanum check 1  # ya completado, sin side-effects de dashboard
```

**Resultado esperado:**
- El check corre normal.
- `ensure_started()` no arranca el server.
- `emit_event` no hace POST ni persiste en `events`.
- `webbrowser.open` no ocurre.
- Confirmar con: `python -c "import sqlite3; c = sqlite3.connect('.quest_progress.db'); print(c.execute('SELECT COUNT(*) FROM events WHERE created_at > datetime(\"now\", \"-1 minute\")').fetchone())"`. Debe ser 0.

Restaurar:

```powershell
Remove-Item Env:\ARKANUM_NO_DASHBOARD
```

---

## 10. Casos de error transversales

### 10.1. SyntaxError en starter

```powershell
# Editar quest_01/starter/main.py: agregar "def broken(:" al final.
arkanum check 1 --dry-run
```

**Resultado esperado:** tabla con un solo check ✘ "Parsea como Python válido" + detalle "El starter tiene un SyntaxError." No crashea el CLI.

Restaurar.

### 10.2. Quest inexistente

```powershell
arkanum start 99
arkanum check 99
arkanum cost
```

**Resultado:**
- `arkanum start 99`: error `BadParameter: No existe quest #99`.
- `arkanum check 99`: lo mismo.
- `arkanum cost`: funciona, no usa N.

### 10.3. BD bloqueada

Para simular: abrir una conexión SQLite write-exclusive en otra terminal:

```powershell
python -c "import sqlite3, time; c = sqlite3.connect('.quest_progress.db'); c.execute('BEGIN EXCLUSIVE'); time.sleep(10)"
```

En la otra terminal, mientras está bloqueada:

```powershell
arkanum progress
```

**Resultado:** `sqlite3.OperationalError: database is locked`. Es esperable — single-user, no esperamos contención.

### 10.4. Puerto ocupado

```powershell
# Otro proceso en puerto 8765
python -m http.server 8765
# En otra terminal:
arkanum dashboard start
```

**Resultado:** el lifecycle prueba 8766, 8767, 8768 hasta encontrar uno libre. Mensaje "Dashboard activo (PID XXXX, puerto 8766)".

### 10.5. SIGINT durante `arkanum run`

```powershell
arkanum run 8 "tarea larga"
# Cuando empiece a iterar, Ctrl+C.
```

**Resultado esperado:**
- Subprocess termina.
- Exit code 130.
- Los steps capturados hasta ese momento están en `agent_traces`.
- `session_end` puede o no estar registrado (depende de cuándo se interrumpió).

### 10.6. `--yes` para CI

```powershell
# Romper un quest, correr check con auto-confirm
arkanum check 7 --yes
```

**Resultado esperado:** pre-checks fallan, se confirma automáticamente (`-y` salta el prompt), procede a invocar Gemini. Útil cuando el CI no puede responder al `typer.confirm`.

---

## 11. Limpieza / reset

```powershell
arkanum dashboard stop
Remove-Item .quest_progress.db -Force
Remove-Item .quest_progress.pid -Force -ErrorAction SilentlyContinue
Remove-Item .quest_dashboard.pid -Force -ErrorAction SilentlyContinue
Remove-Item .quest_dashboard.port -Force -ErrorAction SilentlyContinue
Remove-Item .last_celebrate.timestamp -Force -ErrorAction SilentlyContinue
Remove-Item .setup_cache.json -Force -ErrorAction SilentlyContinue

# Restaurar starters al estado original
git checkout HEAD -- "quests/**/starter/main.py" "common/functions/get_valid_target_path.py" "common/functions/call_function.py" "common/functions/get_file_content.py" "common/functions/write_file.py" "common/functions/run_python_file.py" "common/prompts/system_prompt.py"
```

**Resultado:** repo y BD vuelven al estado pre-test.

---

## 12. Checklist final

Marcar cuando todo lo anterior pase:

- [ ] **0. Setup** — `arkanum init`, dashboard arranca, todas las páginas vacías rinden.
- [ ] **1. Q01** — pistas funcionan en orden, check pasa, celebración con One shot, mapa actualizado.
- [ ] **2. Q02** — primera entrada de costo, pill aparece en perfil.
- [ ] **3. Q03** — argparse + types.Content, args extras se reenvían.
- [ ] **4. Q04** — system prompt + config, **cierre Acto I**, `/milestones` y banner del map.
- [ ] **5. Q05** — validador + starter, dos archivos.
- [ ] **6. Q06** — 3 schemas + Tool registrada.
- [ ] **7. Q07** — `arkanum run` con tracing en vivo en `/live-agent`.
- [ ] **8. Q08** — agent loop completo, **cierre Acto II**.
- [ ] **9. Transversales** — perfil final, accesibilidad, fuentes, lifecycle dashboard.
- [ ] **10. Errores** — SyntaxError, quest inexistente, puerto ocupado, SIGINT.
- [ ] **11. Reset** — vuelta al estado limpio.

**Resultado final esperado:** los 12 grupos marcados. Si alguno falla, abrir issue describiendo paso exacto + comportamiento observado + esperado.
