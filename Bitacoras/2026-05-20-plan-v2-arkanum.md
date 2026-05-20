# Bitácora — Plan v2 del Laboratorio Arkanum

> **Fecha:** 2026-05-20
> **Branch sugerido:** `feat/dashboard-arcano-v2`
> **Estado:** Plan preliminar. v1 cerrado en `4e1aaec` (F17). Cada feature de este plan es independiente y desplegable por separado.
> **Plan canónico de v1:** [`2026-05-19-plan-dashboard-arcano.md`](2026-05-19-plan-dashboard-arcano.md)
> **Avance de v1:** [`avance.md`](avance.md)

---

## 0. Resumen ejecutivo

v1 entregó el laboratorio operativo: 8 quests, 4 actos (2 disponibles), CLI `arkanum`, dashboard arcano con 9 páginas, sistema de pistas, tracking de tiempo/intentos/costo, cierre de acto, visualización del agent loop y accesibilidad básica.

v2 es **expansión pedagógica y de retención**, no refactor estructural. Cada feature suma una capa sobre el sistema existente sin tocar la base. Las features se pueden implementar en cualquier orden — no hay dependencias entre ellas.

**Estimación total:** ~50-60 horas distribuibles en 11 features.

---

## 1. Filosofía v2

Misma de v1, agregando:

| Regla | Consecuencia |
|---|---|
| v2 no reescribe v1 | Cada feature es aditiva; las tablas existentes no cambian su shape |
| Single-user sigue siendo el modo principal | Multi-aprendiz es opt-in con perfil seleccionable, no reemplaza el flujo actual |
| Ningún feature de v2 puede romper los smokes de v1 | El smoke F17 (30 checks) debe seguir verde después de cada feature |
| Las features experimentales (TTS, VSCode) son opt-in via flag | Sin riesgo de degradar el flujo principal |

---

## 2. Decisiones pendientes

Cada feature tiene su sub-decisión. La tabla agregada se completa al planificar cada una en detalle.

| Feature | Decisión clave |
|---|---|
| PDFs de certificado | Banner, layout, firma de Zhyréon |
| Boss del Acto | Mecánica: quiz con tiempo límite vs reto agente vs combinación |
| Grimorio personal | Lista plana vs estructura jerárquica vs grafo de conceptos |
| Glosario contextual | Detección automática (parser) vs lista curada |
| Quiz post-acto | Cantidad de preguntas, formato, generación con LLM vs estática |
| Modo review diff | Diff inline vs side-by-side vs ambos |
| Multi-aprendiz | Selector arriba del nav vs subdominio vs query param |
| Audio TTS | gTTS / ElevenLabs / Coqui local; coste vs latencia vs voz |
| VSCode extension | Web view embebido vs panel nativo |

---

## 3. Stack adicional (a evaluar)

```toml
# Para PDFs (feature 1)
reportlab = "^4.2"
# O bien
weasyprint = "^63.0"

# Para audio TTS (feature 8)
gtts = "^2.5"            # online, gratis, latencia ~1-2s
# o pyttsx3 = "^2.97"    # offline, calidad limitada

# Para quiz con LLM (feature 5)
# Ya tenemos google-genai. Sin deps nuevas.

# Para VSCode extension (feature 9)
# TypeScript fuera del repo Python; el repo expone APIs HTTP suficientes.
```

Ninguna dep es bloqueante — cada feature decide la suya al implementarse.

---

## 4. Features del plan v2

### F-v2.1 — Generación de certificados PDF (~6h)

**Diferido desde:** plan canónico v1 sección 12 (decisión: F-v2 incluye banner + firma).

**Objetivo**
> Done cuando: al cerrarse un acto, se genera un PDF descargable con el nombre del aprendiz, el acto cerrado, la fecha, los rangos obtenidos y la firma estilizada de Zhyréon. Botón "Descargar pergamino" en cada card de `/milestones`.

**Plan**
1. Decidir entre `reportlab` (más control, más código) y `weasyprint` (HTML → PDF, más rápido de prototipar, requiere dependencias del sistema).
2. Template HTML/CSS específico para impresión (paleta más sobria, sin animaciones).
3. Endpoint `GET /milestones/{act_number}/certificate.pdf` que renderiza y sirve.
4. Botón en `milestone-card` con link al endpoint.
5. Persistir el PDF en `data/certificates/act-{N}-{username}.pdf` para servir el mismo blob en future requests.

**Riesgo**
- `weasyprint` necesita librerías nativas (GTK, Pango). En Windows puede ser complicado. `reportlab` es más portable pero requiere reescribir el layout en código Python.

**Recomendación**
- Empezar con `reportlab` por portabilidad. Layout simple: banner del acto + texto centrado + glifo de Zhyréon.

---

### F-v2.2 — Reto / Boss del Acto (~10h)

**Objetivo**
> Done cuando: al completar el último quest de un acto, en lugar de mostrar la celebración estándar, se desbloquea un "Reto del Acto" — una prueba integradora que combina los conceptos de las 4 quests previas. Pasar el reto otorga un rango especial ("Maestro del Acto N") y un logro permanente.

**Plan**
1. Definir mecánica del reto por acto:
   - **Acto I**: agente con system prompt complejo + parser de respuestas (combina Q01-Q04).
   - **Acto II**: agente con tools encadenadas que resuelve una tarea compleja en `<MAX_ITERS`.
2. Carpeta nueva `quests/boss_act_N/` con starter + check + README.
3. Tabla nueva `act_bosses(act_number PK, completed_at, attempts)`.
4. UI: card especial en `/milestones` con estado "Reto disponible / completado".
5. Comando `arkanum boss <act>` análogo a `arkanum start`/`arkanum check`.

**Riesgo**
- Diseño pedagógico exige cuidado: el reto debe sentirse como síntesis, no como "Q05 escondida".
- Si el reto del Acto II requiere un agente más sofisticado, podría ser frustrante. Mantenerlo cerca del nivel de Q08.

---

### F-v2.3 — Grimorio personal (~4h)

**Objetivo**
> Done cuando: existe una página `/grimoire` que lista los conceptos desbloqueados por el aprendiz, agrupados por acto. Cada concepto enlaza a la entrada relevante del Códex. Los conceptos se "desbloquean" automáticamente al completar el quest que los introduce.

**Plan**
1. Tabla nueva `concept_unlocks(concept_id, quest_id, unlocked_at)`.
2. Mapeo estático `quest → concepts[]` en `quest_catalog.py` (ej. Q01 → ["genai.Client", "generate_content"], Q03 → ["argparse", "types.Content"], etc.).
3. Hook en `record_quest_completion`: insertar conceptos del quest.
4. `/grimoire` agrupa por acto, lista con links a `/codex/...`.
5. Pill "Grimorio: N conceptos" en perfil.

**Riesgo**
- Mantenimiento del mapeo: si se renombra una entrada del Códex, el link rompe. Validar al cargar el catálogo.

---

### F-v2.4 — Glosario contextual con tooltips (~5h)

**Objetivo**
> Done cuando: dentro de READMEs y entradas del Códex, ciertos términos clave (`function_call`, `usage_metadata`, `types.Content`, etc.) tienen un tooltip al hacer hover con su definición corta + link al Códex.

**Plan**
1. Diccionario JSON `common/dashboard/static/glossary.json` con `{ termino: { definicion, link } }`.
2. Post-procesador en `services/markdown.py` que envuelve cada match (case-sensitive) en `<span class="glossary-term" data-term="..."></span>`.
3. JS que detecta hover y muestra tooltip con `position: fixed`.
4. Estilo: subrayado punteado dorado discreto.
5. Configurable: si el aprendiz está en Q01-Q03, sólo se marcan términos básicos; si está en Q07+, también términos avanzados.

**Riesgo**
- El parser de markdown podría romper si los términos aparecen dentro de bloques de código. Excluir `<code>` y `<pre>` del matching.
- Demasiados tooltips abruman. Mantener máximo 8-10 términos por nivel.

---

### F-v2.5 — Quiz / flashcards post-acto (~6h)

**Objetivo**
> Done cuando: al cerrar un acto, además del `/celebrate` estándar y el certificado PDF, el aprendiz puede tomar un quiz de 5 preguntas multi-choice sobre los conceptos del acto. Pasar 4/5 desbloquea un logro "Iniciado del Acto N".

**Plan**
1. JSON estático `quests/boss_act_N/quiz.json` con preguntas + opciones + correcta.
2. Tabla `quiz_attempts(act_number, score, attempted_at)`.
3. Página `/quiz/{act}` con flow "una pregunta a la vez" + barra de progreso.
4. Logro nuevo `iniciado_act_N` en `services/achievements.py`.

**Riesgo**
- Generar preguntas con LLM es tentador (variabilidad), pero requiere cuota. v2.5 arranca con preguntas estáticas; v2.5.1 puede agregar generación dinámica.

---

### F-v2.6 — Modo "review" diff con solución oficial (~4h)

**Objetivo**
> Done cuando: tras pasar un check, el aprendiz puede ver `arkanum review N` o ir a `/quest/{slug}#review` para comparar su `starter/main.py` con `solution/solution.py` (o `solution/main.py`) en formato diff side-by-side. Sólo visible **después** de pasar el quest.

**Plan**
1. Servicio `services/diff.py` con `unified_diff(starter, solution)` usando `difflib`.
2. Endpoint `GET /api/quests/{slug}/review` (sólo si completed → 200; si no → 403).
3. Tab nueva en `quest_view.html` "Tu solución vs oficial".
4. Comando `arkanum review <N>` con render Rich del diff.

**Riesgo**
- La "solución oficial" no es la única correcta. Aclarar en el header que es **una** solución de referencia, no LA solución.

---

### F-v2.7 — Multi-aprendiz (~5h)

**Objetivo**
> Done cuando: la tabla `apprentice` permite múltiples filas; el dashboard expone un selector arriba del nav para cambiar de perfil; el CLI acepta `--profile <name>` o usa el último activo. Todas las tablas con `quest_id` se prefijan implícitamente por `apprentice_id`.

**Plan**
1. Quitar el `CHECK (id = 1)` de la tabla `apprentice`.
2. Agregar `apprentice_id` (FK) a todas las tablas relacionadas (`quest_completion`, `quest_progress`, `quest_attempts`, `hint_usage`, `quest_reading`, `act_milestones`, `quest_costs`, `agent_traces`).
3. Migración: para BD existente, asignar `apprentice_id = 1` a todas las rows.
4. Archivo `.arkanum/active_profile` que recuerda el último perfil usado.
5. Selector en `base.html` con dropdown.
6. Comando `arkanum profile [list|create|switch <name>|delete <name>]`.

**Riesgo**
- Migración de BD es la parte delicada. Si falla a mitad, deja la BD en estado inconsistente. Wrap en transacción + script `arkanum migrate` con confirmación.
- Multi-aprendiz puede confundir a quien venga con expectativa single-user. Mantener defaults sin cambios cuando hay un solo perfil.

---

### F-v2.8 — Audio narration TTS de Zhyréon (~6h)

**Objetivo**
> Done cuando: las quotes de Zhyréon en `/celebrate`, `/milestones` y headers de actos tienen un botón "🔊 Escuchar" que las reproduce con una voz consistente. Audio se cachea en `data/audio/` para que el mismo texto no se regenere.

**Plan**
1. Elegir motor TTS:
   - **gTTS** (Google, online, gratis, voz "es-es" estándar): simple, requiere red.
   - **pyttsx3** (offline, voz del SO): garbage en algunos sistemas.
   - **ElevenLabs** (online, pago, calidad alta + voces customizadas): si el budget lo permite, ideal para "voz de Zhyréon" consistente.
2. Helper `services/tts.py` con `synthesize(text) → audio_bytes` + cache por SHA-256 del texto.
3. Endpoint `GET /api/tts?text=...&voice=zhyreon` que devuelve `audio/mpeg`.
4. Botón en templates con `<audio>` HTML5.

**Riesgo**
- ElevenLabs es la mejor calidad pero introduce un costo monetario. v2.8 arranca con gTTS y deja el slot para upgrade.
- Audio offline (pyttsx3) suena artificial — choca con la estética arcana.

---

### F-v2.9 — VSCode extension (~10h)

**Objetivo**
> Done cuando: una extensión `arkanum-quest` para VSCode muestra el dashboard arcano en un panel WebView lateral. Comandos de la paleta: "Arkanum: Iniciar quest actual", "Arkanum: Validar quest actual", "Arkanum: Pedir pista". Status bar muestra XP / nivel / quest actual.

**Plan**
1. Proyecto separado en `vscode-extension/` (TypeScript).
2. WebView que carga `http://127.0.0.1:8765` (arranca el server si no está).
3. Comandos VSCode que invocan `arkanum start|check|...` vía task runner.
4. Status bar item con polling a `/api/setup/status`.
5. Publicación al Marketplace (opcional).

**Riesgo**
- Mantenimiento de una extensión TypeScript exige skill set distinto. Si el equipo solo tiene Python, considerar diferir a v3.
- Marketplace tiene proceso de aprobación. Empezar con extension local (`.vsix` sideload).

---

### F-v2.10 — Logros adicionales (~3h)

**Objetivo**
> Done cuando: el catálogo de logros se amplía con 3-5 logros nuevos, calculados on-the-fly como los actuales. Aparecen en perfil, quest view y celebrate.

**Candidatos**
- **Erudito** — `mark_read` en los 8 READMEs.
- **Cazador** — completar las 4 quests del Acto I sin pedir ninguna pista en ninguna (escala de "Sin red" a acto completo).
- **Inquebrantable** — completar el acto sin pasar más de 2 intentos en ningún quest.
- **Madrugador** — completar un quest dentro de los primeros 60 segundos del `first_attempt_at`.
- **Maratón** — sesión de 4+ quests completados en el mismo día.

**Descartado**
- ~~**Velocista**~~ (`total_time_seconds < 600`) — incentiva trampear el reloj cerrando y reabriendo. Documentado en v1 F13.

**Riesgo**
- Demasiados logros diluyen el peso de cada uno. Curar a 3-4 nuevos máximo.

---

### F-v2.11 — Mejoras menores de v1 (~2h)

Items pequeños que no justifican una feature propia:

- **Auto-scroll toggle en `/live-agent`**: botón "🔒 Fijar al final / 🔓 Liberar" para que el aprendiz pueda revisar steps anteriores sin que el polling lo arrastre al final.
- **"Tiempo total del acto" agregado en `/milestones`**: suma de `total_time_seconds` de las quests del acto, formateado con el filter `format_duration` de F13.
- **Toast del `act_closed`** en el perfil: extender `pollToast` en `dashboard.js` para incluir `kind === "act_closed"` con CTA a `/milestones`.

---

## 5. Roadmap sugerido

No hay dependencias técnicas entre features. El orden recomendado prioriza valor pedagógico × esfuerzo:

| # | Feature | Esfuerzo | Valor | Notas |
|---|---|---|---|---|
| 1 | F-v2.11 — Mejoras menores | 2h | 🟢 Alto | Quick wins, sin riesgo |
| 2 | F-v2.10 — Logros adicionales | 3h | 🟢 Alto | Refuerza retención |
| 3 | F-v2.3 — Grimorio personal | 4h | 🟢 Alto | Visualiza progreso conceptual |
| 4 | F-v2.6 — Modo review diff | 4h | 🟢 Alto | Cierra el loop pedagógico post-quest |
| 5 | F-v2.5 — Quiz post-acto | 6h | 🟡 Medio | Profundiza conceptos del acto |
| 6 | F-v2.4 — Glosario contextual | 5h | 🟡 Medio | UX placentera, no transformadora |
| 7 | F-v2.1 — PDFs de certificado | 6h | 🟡 Medio | Tangibilidad del logro |
| 8 | F-v2.7 — Multi-aprendiz | 5h | 🟠 Bajo | Útil para profesores/equipos |
| 9 | F-v2.2 — Boss del Acto | 10h | 🟡 Medio | Capstone por acto, alto esfuerzo |
| 10 | F-v2.8 — Audio TTS | 6h | 🟠 Bajo | Inmersión, requiere coste o calidad |
| 11 | F-v2.9 — VSCode extension | 10h | 🟠 Bajo | Útil pero requiere skill TS |

**MVP de v2** (features 1-5): ~19h → quick wins + grimorio + review + quiz.
**v2 completo**: ~61h.

---

## 6. Reglas operativas

1. **Cada feature cierra con un commit** `feat(v2): F-v2.N - <descripcion>` + un commit `docs(bitacora-v2): fijar hash <hash> para F-v2.N` (mismo patrón que v1).
2. **Smoke regresión de v1 debe seguir verde** después de cada feature. Si una migración rompe los smokes, revertir y replantear.
3. **`avance.md` original (v1) no se toca**. Crear `avance-v2.md` que sigue el mismo formato pero arranca con tabla vacía.
4. **Compat con BD v1**: cualquier migración aditiva (CREATE TABLE IF NOT EXISTS, ADD COLUMN). No DROP, no RENAME.
5. **Cada feature documenta su decisión de diseño en su sección** del plan antes de implementar (lo que está aquí es preliminar).

---

## 7. Diferido a v3

(Anticipa, no compromete.)

- Quests del Acto III (Inteligencia Extendida): RAG, embeddings, vector stores.
- Quests del Acto IV (Arquitectura de Agentes): multi-agente, supervisión, orquestación.
- Modo "creador": permitir al aprendiz autor de quests definir las suyas.
- Sincronización con backend remoto (multi-device para el mismo aprendiz).
- Internacionalización (`es` → `en`, `pt`).

---

## 8. Siguiente paso

Cuando se inicie v2:

1. Crear branch `feat/dashboard-arcano-v2` desde `feat/dashboard-arcano` (último commit `7575037` o más reciente).
2. Crear `Bitacoras/avance-v2.md` con la misma estructura que `avance.md` pero arrancando vacío.
3. Elegir la primera feature del roadmap (sugerencia: F-v2.11 — mejoras menores para warm-up).
4. Detallar su decisión de diseño en este archivo, implementar, smoke, commit, fijar hash.
