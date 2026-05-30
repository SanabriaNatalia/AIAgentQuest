# Bitácora — Pruebas del Live Agent (perspectiva del aprendiz)

> **Fecha:** 2026-05-29
> **Branch:** `feat/dashboard-arcano`
> **Alcance:** validación funcional del visualizador `/live-agent` siguiendo el mismo flujo que usaría un aprendiz que termina la Quest 08.
> **Plan que valida:** [`2026-05-22-plan-live-agent-mejoras.md`](2026-05-22-plan-live-agent-mejoras.md)

---

## 0. Filosofía de esta bitácora

Aquí **no se inspeccionan headers HTTP, ni se editan archivos de la DB, ni se abre DevTools**. Cada caso de prueba se ejecuta con dos herramientas:

1. La terminal (comandos `arkanum *`).
2. El navegador apuntando a `http://127.0.0.1:8765`.

Si una mejora exige tocar algo que un aprendiz no tocaría jamás, no entra en esta suite. Lo que sí queda es **funcional**: cada paso verifica un comportamiento observable desde la UI o el CLI.

---

## 1. Prerequisitos (qué tienes que tener listo antes)

### 1.1 Camino del aprendiz hasta este punto

El Live Agent solo es relevante a partir de la Quest 07 (el agente ya manifiesta su voluntad con tools). Antes de probar nada, el aprendiz debería tener completadas:

| Quest | Por qué importa para estas pruebas |
|---|---|
| Q01 — First Invocation | Verifica que `GEMINI_API_KEY` funciona y el cliente de Gemini está instanciado. |
| Q02 — Words of Power     | El prompt llega al modelo. |
| Q03 — Voice of Power     | Argparse y CLI básico — el wrapper `arkanum run` reenvía args al starter. |
| Q04 — Persona Manifest   | `common/prompts/system_prompt.py` ya tiene contenido propio (no es el placeholder). |
| Q05 — Echo of Knowledge  | Comprensión de tokens / costos — los KPIs del HUD tendrán sentido. |
| Q06 — Tool Chest         | Tools declaradas en `common/functions/call_function.py`. |
| Q07 — Agent Incarnation  | El agente ejecuta tools de verdad. Aquí se ven `function_call` / `function_result` por primera vez. |
| Q08 — Manifesting Cycle  | El loop iterativo. Es la quest pensada para esta bitácora. |

**Verificación rápida:** abre `http://127.0.0.1:8765/profile` y confirma que Q07 y Q08 figuran como completadas o en curso. Si Q08 está bloqueada, no podrás disparar el flujo principal del Live Agent.

### 1.2 Setup del entorno

| # | Requisito | Cómo verificarlo |
|---|---|---|
| 1.2.1 | Repo clonado y branch `feat/dashboard-arcano` | `git status` muestra `On branch feat/dashboard-arcano` |
| 1.2.2 | Dependencias instaladas | `uv sync` corre sin error |
| 1.2.3 | Archivo `.env` con `GEMINI_API_KEY=...` válido | `arkanum check 1` no se queja por API key |
| 1.2.4 | Puerto 8765 libre (lo necesita el dashboard) | Cierra cualquier `arkanum dashboard` previo |
| 1.2.5 | Existe `quests/quest_07_agent_incarnation/workspace/notes.txt` con texto | Si no, créalo con cualquier contenido (p.ej. "lista de la compra: pan, leche, café") |

### 1.3 Solución de Q08 — quién la corre

Las mejoras `agent_thought`, `iteration_start`, `latency`, `context_growth` y `agent_final` se emiten desde la **solución** de Q08, no desde el starter del aprendiz. Eso quiere decir:

- Si vas a probar a fondo el visualizador, ejecuta la solución:
  `arkanum run 8 "..."` lanza por defecto el starter del aprendiz. Para forzar la solución, mira el bloque H.
- Si corres tu propio starter de Q08, verás `function_call` / `function_result` (por el parser de stdout) pero no verás pensamiento ni bandas ni costo por iteración. Eso es esperado.

Atajo recomendado para esta suite: copia el contenido de `quests/quest_08_manifesting_cycle/solution/solution.py` dentro de tu `starter/main.py` antes de empezar, para que `arkanum run 8` ejecute la versión instrumentada.

### 1.4 Arranca el dashboard una sola vez

En una terminal dedicada:

```powershell
arkanum dashboard
```

Deja esa terminal abierta durante toda la suite. Cualquier otro comando va en otra terminal.

Abre `http://127.0.0.1:8765/live-agent` en el navegador y déjalo abierto.

---

## 2. Convenciones de cada caso

```
### TC-XX — Nombre
Cubre: mejora(s) #N
Precondición: estado antes del test
Pasos: numerados, todos hacibles desde CLI o navegador
Qué deberías ver: descripción concreta de la UI
Estado: [ ] no probado · [x] OK · [!] falla
```

Marca el estado al ejecutar. Si algo falla, anota en el bloque final con fecha y síntoma.

---

## 3. Bloque A — Primera vista de `/live-agent`

### TC-A1 — La página carga limpia
**Cubre:** wiring general
**Precondición:** dashboard arrancado (1.4).
**Pasos:**
1. Abre `http://127.0.0.1:8765/live-agent`.
2. Recarga (F5).
**Qué deberías ver:**
- Encabezado "Agente en directo".
- Toolbar con el texto "Esperando trace…" y un punto de color glow pulsando.
- Un bloque colapsado "▶ Lanzar nuevo prompt" en glow.
- Un bloque "Historial" que dice "(sin ejecuciones)" o muestra cards previas si ya corriste algo.
- Un HUD horizontal con 5 cifras: Iteraciones (0), Tools (0), Tokens (0), Costo (USD) ($0.0000), Latencia ⌀ (—).
- Dos paneles desplegables: "Prompt del usuario" y "System prompt".
- Más abajo, un panel grande explicando cómo usar `arkanum run`.

**Estado:** [ ]

### TC-A2 — El system prompt se ve sin tocar nada
**Cubre:** mejora #10
**Pasos:**
1. Click sobre el panel "System prompt".
**Qué deberías ver:**
- El bloque se expande y muestra el contenido completo del archivo `common/prompts/system_prompt.py`.
- Si el archivo todavía tiene el placeholder ("Escribe tu prompt del sistema aquí…"), aparece una nota dorada: "Este archivo todavía contiene el placeholder. La Quest 04 te pide reescribirlo."
- Si ya escribiste tu propio system prompt en Q04, no aparece esa nota.

**Estado:** [ ]

---

## 4. Bloque B — Tu primer trace en vivo

### TC-B1 — Lanza un agente desde la terminal y ve los pasos en el navegador
**Cubre:** mejoras #9, #10, #12, #13
**Precondición:** TC-A1 verde, otra terminal disponible.
**Pasos:**
1. En la segunda terminal:
   ```powershell
   arkanum run 8 "Lee notes.txt y dime qué contiene"
   ```
2. Cambia al navegador en `/live-agent` y observa.

**Qué deberías ver (todo en vivo, sin recargar):**
- El toolbar pasa de "Esperando trace…" a "Trace abc123" (un ID de 12 chars).
- En el panel "Prompt del usuario", la preview muestra "Lee notes.txt y dime qué contiene".
- El HUD comienza a moverse: Iteraciones 1, Tools 1, Tokens >0, Costo creciente, Latencia con un número.
- Aparece una **banda horizontal** "Iteración 1 / 20" con un meta que dice algo como `2.40 s · 1.2k tokens · $0.0003`.
- Dentro de la banda hay tarjetas. Al menos una con icono 🧠 y texto en italic (pensamiento), y otra con ⚡ y nombre de función (function_call).
- Cuando termina, la última tarjeta es una respuesta final con icono ✦.

**Estado:** [ ]

### TC-B2 — El pensamiento del agente es legible
**Cubre:** mejora #9
**Precondición:** TC-B1 verde.
**Pasos:**
1. En el trace que acabas de generar, busca la tarjeta con icono 🧠.
**Qué deberías ver:**
- El texto es prosa en italic, no código.
- Se lee como una explicación humana: "voy a leer notes.txt para entender qué pide el usuario" o similar.
- Si no aparece esta tarjeta, verifica que estás ejecutando la solución de Q08 (ver 1.3).

**Estado:** [ ]

### TC-B3 — La latencia aparece en cada banda
**Cubre:** mejora #12
**Pasos:** mira el meta del header de cada banda "Iteración N".
**Qué deberías ver:** un tiempo en segundos (por ejemplo `2.40 s`). Si el modelo tardó mucho en alguna iteración, esa banda tendrá un número más alto. La media también está en el HUD bajo "Latencia ⌀".

**Estado:** [ ]

---

## 5. Bloque C — Visualización del loop (pairing y bandas)

### TC-C1 — Una tool ejecutándose muestra spinner hasta que llega su resultado
**Cubre:** mejora #2
**Pasos:**
1. Lanza un prompt que dispare varias tools:
   ```powershell
   arkanum run 8 "Lee los archivos del workspace y dime cuál es más largo"
   ```
2. Observa rápidamente las tarjetas con icono ⚡ mientras llegan.

**Qué deberías ver:**
- Al inicio cada `function_call` aparece con un pequeño spinner girando y texto "ejecutando…".
- Cuando llega el resultado, el spinner desaparece y debajo aparece un bloque verde "Resultado" con el payload.
- Cada tool ocupa una sola tarjeta (no dos).

**Estado:** [ ]

### TC-C2 — Las bandas dividen las iteraciones del loop
**Cubre:** mejora #3
**Pasos:** mira el trace completo de TC-C1.
**Qué deberías ver:** varias bandas "Iteración 1 / 20", "Iteración 2 / 20", etc. Cada banda agrupa el pensamiento + las tools llamadas en esa vuelta. Es la representación visual del `for _ in range(MAX_ITERS):` de Q08.

**Estado:** [ ]

### TC-C3 — El prompt del usuario queda registrado en el panel
**Cubre:** mejora #10
**Pasos:**
1. Lanza:
   ```powershell
   arkanum run 8 "Mi prompt único de prueba 2026-05-29"
   ```
2. En el navegador, mira la preview del panel "Prompt del usuario".

**Qué deberías ver:** el texto "Mi prompt único de prueba 2026-05-29" en la preview, truncado a ~60 chars. Al hacer click se expande y se ve completo.

**Estado:** [ ]

---

## 6. Bloque D — Telemetría: costo, contexto, HUD

### TC-D1 — El HUD acompaña la ejecución
**Cubre:** mejora #13
**Pasos:** mientras un `arkanum run 8` está corriendo, mira los 5 KPIs del HUD.
**Qué deberías ver:**
- `Iteraciones` sube de 0 a N a medida que el loop avanza.
- `Tools` sube cada vez que el agente llama una herramienta.
- `Tokens` y `Costo (USD)` crecen monotónicamente.
- `Latencia ⌀` se actualiza con la media de las llamadas.

**Estado:** [ ]

### TC-D2 — Cada banda muestra su costo
**Cubre:** mejora #6
**Pasos:** en un trace completo, lee el meta de cada banda.
**Qué deberías ver:** `Iteración N · X.XX s · Yk tokens · $Z.ZZZZ`. La suma de los `$` de cada banda debería coincidir aproximadamente con el `Costo (USD)` del HUD.

**Estado:** [ ]

### TC-D3 — El contexto crece visiblemente
**Cubre:** mejora #11
**Pasos:**
1. Al final de cada banda, busca un panel pequeño "🗂 Contexto: N messages".
2. Compara el número entre la iteración 1 y la 2 (y 3 si hay).

**Qué deberías ver:** el número sube cada iteración. Es la memoria del loop creciendo (`messages` en el código del aprendiz).

**Estado:** [ ]

### TC-D4 — Puedes ver qué cambió en el contexto
**Cubre:** mejora #17
**Pasos:** haz click sobre uno de los paneles "🗂 Contexto: N messages".
**Qué deberías ver:** una lista de los items nuevos en esa iteración. Cada línea muestra `role` (user, model, tool…) y `kind` (text, function_call, function_response) con un preview corto. Esto te muestra exactamente qué entró al historial.

**Estado:** [ ]

---

## 7. Bloque E — Historial y replay

### TC-E1 — El historial te muestra varias ejecuciones
**Cubre:** mejora #4
**Pasos:**
1. Lanza tres prompts seguidos, esperando que cada uno termine:
   ```powershell
   arkanum run 8 "prueba A"
   arkanum run 8 "prueba B"
   arkanum run 8 "prueba C"
   ```
2. Mira el panel "Historial" en `/live-agent`.

**Qué deberías ver:**
- Tres cards horizontales.
- La más reciente está marcada "● en vivo" en glow; las anteriores como "○ histórico".
- Cada card muestra el prompt truncado, el número de pasos y el tiempo relativo ("X s atrás").

**Estado:** [ ]

### TC-E2 — Puedes navegar a una ejecución pasada con un click
**Cubre:** mejora #4
**Pasos:** en el historial, click sobre la card de "prueba B".
**Qué deberías ver:**
- La card se resalta con un borde glow.
- El área de pasos se vacía y se rerenderiza con los pasos de "prueba B".
- El HUD recalcula sus KPIs para esa ejecución.
- En el panel "Prompt del usuario" aparece "prueba B".

**Estado:** [ ]

### TC-E3 — Vuelves a la ejecución viva con otro click
**Cubre:** mejora #4
**Pasos:** desde TC-E2, click en la primera card ("● en vivo").
**Qué deberías ver:** vuelve a mostrar el trace más reciente; el polling deja de filtrar por el ID histórico.

**Estado:** [ ]

### TC-E4 — Puedes reproducir un trace en cámara lenta
**Cubre:** mejora #14
**Pasos:**
1. Asegúrate de tener un trace seleccionado (uno completo).
2. Click en el botón "▶ Replay" arriba a la derecha.
3. Cuando pregunte la velocidad, escribe `1` y acepta.

**Qué deberías ver:** los pasos se redibujan en orden, con los mismos tiempos relativos que tuvieron originalmente (capeado a 3 s entre pasos para no aburrir). A `1` se siente como ver el original otra vez. A `4` va cuatro veces más rápido. A `999` es instantáneo.

**Estado:** [ ]

---

## 8. Bloque F — Modo explicador y export

### TC-F1 — El modo explicador añade tooltips pedagógicos
**Cubre:** mejora #15
**Pasos:**
1. Marca el checkbox "📖 Explicador" del toolbar.
2. Mira las tarjetas.

**Qué deberías ver:** cada tipo de paso (function_call, function_result, agent_thought, latency, tokens, context_growth…) muestra debajo, en italic gris, una explicación corta. Las bandas también traen su explicación.

**Estado:** [ ]

### TC-F2 — La preferencia del explicador se mantiene al recargar
**Cubre:** mejora #15
**Pasos:**
1. Con el explicador activo, recarga la página (F5).

**Qué deberías ver:** el checkbox sigue marcado y los tooltips siguen visibles. La preferencia vive en el navegador (localStorage).

**Estado:** [ ]

### TC-F3 — Puedes copiar el trace como markdown para compartirlo
**Cubre:** mejora #16
**Pasos:**
1. Click en "📋 Markdown" del toolbar.
2. Pega el contenido en cualquier editor (Notepad, VS Code, Discord…).

**Qué deberías ver:**
- El botón parpadea con "✓ Copiado".
- En el editor donde pegues, ves un markdown con cabecera (Trace ID, quest, pasos), una `## Iteración N` por banda, y cada paso como bullet con icono.

**Estado:** [ ]

### TC-F4 — Puedes descargar el trace como JSON
**Cubre:** mejora #16
**Pasos:** click en "💾 JSON".
**Qué deberías ver:** se descarga un archivo `trace_<id>.json`. Al abrirlo en un editor, contiene la lista cruda de pasos. Sirve para archivar o compartir un caso técnico.

**Estado:** [ ]

---

## 9. Bloque G — Editor del system prompt

> Aviso: este bloque modifica el archivo `common/prompts/system_prompt.py`. El editor crea un backup automático en `system_prompt.py.bak` antes de tocar el original. Al final del bloque, restaura tu versión.

### TC-G1 — Editar y guardar un nuevo system prompt
**Cubre:** mejora #18
**Pasos:**
1. Abre el panel "System prompt" en `/live-agent`.
2. Click en "✏ Editar".
3. Cambia el contenido por:
   ```
   Eres un agente que responde siempre en mayúsculas. TEST 2026-05-29.
   ```
4. Click en "💾 Guardar".

**Qué deberías ver:**
- La página recarga sola.
- Al volver a abrir el panel "System prompt", aparece el nuevo contenido.
- En la carpeta `common/prompts/`, ahora existe `system_prompt.py.bak` con la versión anterior.

**Estado:** [ ]

### TC-G2 — El cambio se aplica al próximo `arkanum run`
**Cubre:** mejora #18 (efecto end-to-end)
**Pasos:**
1. Con el system prompt en mayúsculas (TC-G1), lanza:
   ```powershell
   arkanum run 8 "describe los archivos del workspace"
   ```

**Qué deberías ver:** la respuesta final viene en mayúsculas (o intenta forzarlas), confirmando que el cambio del prompt sí entró en la siguiente ejecución del agente.

**Estado:** [ ]

### TC-G3 — El editor rechaza contenido que rompería el archivo
**Cubre:** mejora #18 (validación)
**Pasos:**
1. Abre el editor del system prompt y escribe un texto que contenga `"""` literal.
2. Click en "💾 Guardar".

**Qué deberías ver:** alert con "El contenido no puede incluir comillas triples". El archivo en disco no cambia.

**Estado:** [ ]

### TC-G4 — Restaurar tu system prompt
**Pasos:** en una terminal:
```powershell
Copy-Item common\prompts\system_prompt.py.bak common\prompts\system_prompt.py -Force
```
**Qué deberías ver:** `arkanum run 8 "..."` vuelve a comportarse como antes de TC-G1.

**Estado:** [ ]

---

## 10. Bloque H — Lanzar desde el dashboard

### TC-H1 — Disparar `arkanum run` sin abrir terminal
**Cubre:** mejora #7
**Pasos:**
1. En `/live-agent`, abre el panel "▶ Lanzar nuevo prompt".
2. Deja Quest 8 seleccionada.
3. Escribe en el input: `ping desde el dashboard`.
4. Click en "▶ Ejecutar".

**Qué deberías ver:**
- Bajo el form, mensaje: "✓ Subprocess lanzado. Pasos llegando…".
- En unos segundos empiezan a aparecer pasos como si lo hubieras lanzado desde la terminal.
- El historial añade una card nueva con prompt "ping desde el dashboard".
- No abriste ninguna terminal nueva.

**Estado:** [ ]

### TC-H2 — El botón valida que el prompt no esté vacío
**Cubre:** mejora #7
**Pasos:** en el form, deja el input vacío y pulsa "▶ Ejecutar".
**Qué deberías ver:** el navegador bloquea el envío (campo requerido). El status no muestra ningún "lanzado".

**Estado:** [ ]

### TC-H3 — Puedes lanzar dos prompts seguidos
**Cubre:** mejora #7
**Pasos:**
1. Lanza desde el form: `dame los nombres de archivos`.
2. Inmediatamente lanza: `dame los tamaños`.

**Qué deberías ver:** ambos traces aparecen en el historial. La UI muestra el último por defecto. Click en la card del primero te lleva a su trace.

**Estado:** [ ]

---

## 11. Bloque I — Cierre y estados especiales

### TC-I1 — Cuando el agente termina, el trace queda "sellado"
**Cubre:** mejora #5
**Pasos:** espera a que cualquier `arkanum run 8` termine de imprimir "Final response: …".
**Qué deberías ver:**
- El borde del toolbar pasa a verde.
- El punto del estado deja de pulsar y queda verde.
- El meta dice algo como `... · sellado`.

**Estado:** [ ]

### TC-I2 — Si matas el agente con Ctrl+C, el trace queda "stale"
**Cubre:** mejora #5
**Pasos:**
1. Lanza:
   ```powershell
   arkanum run 8 "Lee notes.txt y luego dime un chiste largo"
   ```
2. Cuando empiece a procesar la segunda iteración (ves la banda "Iteración 2"), pulsa Ctrl+C en la terminal.
3. Vuelve al navegador y espera ~30 s sin hacer nada.

**Qué deberías ver:**
- El borde del toolbar pasa a rojo.
- El punto del estado pasa a rojo.
- El meta dice algo como `... · stale (XXs sin actividad)`.

**Estado:** [ ]

### TC-I3 — El visualizador no se vuelve loco con muchas iteraciones
**Cubre:** robustez general
**Pasos:**
1. Lanza un prompt que requiera muchas iteraciones (por ejemplo "lee cada archivo del workspace, cuenta sus líneas y dime la suma").
2. Mira el navegador mientras procesa.

**Qué deberías ver:** los pasos siguen apareciendo fluidamente. El HUD se actualiza. No hay congelamientos. El scroll automático te lleva al último paso. Si el agente alcanza MAX_ITERS sin respuesta final, ves el mensaje "Maximum iterations (20) reached." en la terminal y el toolbar queda sellado igual.

**Estado:** [ ]

---

## 12. Matriz de cobertura

| Mejora | Casos que la prueban |
|---|---|
| #1  Emisor estructurado    | B1, B2 (efecto indirecto) |
| #2  Pairing call↔result    | C1 |
| #3  Bandas por iteración   | C2 |
| #4  Historial              | E1, E2, E3 |
| #5  Stale / sealed         | I1, I2 |
| #6  Costo por iteración    | D2 |
| #7  Lanzar desde dashboard | H1, H2, H3 |
| #8  Polling adaptativo     | B1, I1 (efecto observable: cuando termina, deja de pulsar) |
| #9  Pensamiento            | B1, B2 |
| #10 Prompts visibles       | A2, B1, C3 |
| #11 Contexto creciente     | D3 |
| #12 Latencia               | B3, D1 |
| #13 HUD sticky             | D1 |
| #14 Replay                 | E4 |
| #15 Modo explicador        | F1, F2 |
| #16 Export                 | F3, F4 |
| #17 Diff de contexto       | D4 |
| #18 Editor system prompt   | G1, G2, G3 |

Cualquier mejora con cero casos verdes implica cobertura insuficiente.

---

## 13. Resultado consolidado

Al terminar, llena esta tabla:

| Bloque | Total | OK | Falla | No probado |
|---|---:|---:|---:|---:|
| A — Primera vista       | 2  | | | |
| B — Tu primer trace     | 3  | | | |
| C — Visualización loop  | 3  | | | |
| D — Telemetría          | 4  | | | |
| E — Historial y replay  | 4  | | | |
| F — Explicador / export | 4  | | | |
| G — Editor system prompt | 4 | | | |
| H — Lanzar desde dash   | 3  | | | |
| I — Cierre y especiales | 3  | | | |
| **Total**               | **30** | | | |

**Criterio de aprobación:** todos los bloques A–E en verde + al menos un caso por mejora + ningún caso de cierre (I1, I2) rojo. Los bloques F, G, H son opcionales si solo quieres validar el flujo central de visualización.

---

## 14. Registro de fallos encontrados

> Anota cada fallo como: `TC-XX · fecha · síntoma · pendiente / resuelto-en-<commit>`.

- (vacío)

---

## 15. Notas finales

- Esta bitácora asume conocimiento de aprendiz post-Q06 (sabe qué es una tool, un function_call, un loop iterativo, una API key).
- Si alguna prueba falla en un entorno limpio, lo más probable es que falte algo del bloque 1 (prerequisitos): API key, contenido del workspace, solución de Q08 sin copiar al starter, etc. Revisa esa lista antes de reportar como bug.
- Cuando se agreguen mejoras nuevas (post-#18), añade su caso al bloque que corresponda y actualiza la matriz de cobertura.
