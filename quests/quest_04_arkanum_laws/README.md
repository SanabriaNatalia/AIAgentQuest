# Quest 04 — Las Leyes del Arkanum

<p align="center">
    <img src="../../assets/images/quest-4-banner.png" alt="Quest 4 Banner" width="100%">
</p>

> *“Todo agente obedece primero las leyes que le dieron forma.”*  
> — Zhyréon

## Información del Quest

| Dificultad | Tiempo estimado |
|---|---|
| 🟢 Fácil | 10–15 mins |

---

## Objetivo

Hasta ahora nuestro agente solo responde directamente a lo que el usuario escribe.

Pero los agentes modernos normalmente tienen una capa adicional de instrucciones:
las reglas internas que definen cómo deben comportarse.

En este Quest aprenderás a utilizar un **system prompt**.

---

## Qué aprenderás

- qué es un system prompt
- diferencia entre instrucciones del sistema y prompts del usuario
- cómo controlar el comportamiento del modelo
- cómo usar `GenerateContentConfig`
- cómo crear respuestas más determinísticas usando `temperature`

---

## ¿Qué es un system prompt?

El [system prompt](../../docs/LLMs/system_prompts.md) es una instrucción especial enviada al modelo antes de la conversación.

Normalmente se utiliza para:
- definir personalidad
- establecer reglas
- restringir comportamiento
- controlar formato de salida
- dar contexto persistente

Por ejemplo:

```text
Eres un mentor especializado en agentes IA.
Responde de forma breve y clara.
```

---

## Prioridad de instrucciones

En muchos modelos conversacionales, las instrucciones del sistema tienen mayor prioridad que los prompts del usuario.

Por ejemplo:

```text
System prompt:
"Responde únicamente: EL LABORATORIO ESCUCHA."

User prompt:
"¿Cuál es la capital de Francia?"
```

↓

```text
"EL LABORATORIO ESCUCHA."
```

---

## Configuración del modelo

En Gemini, el system prompt se envía utilizando:

```python
types.GenerateContentConfig
```

Ejemplo:

```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=messages,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt
    ),
)
```

---

## Temperatura

Los modelos de lenguaje no siempre producen exactamente la misma respuesta.

La [temperatura](../../docs/LLMs/temperature.md) controla el nivel de variabilidad.

Valores bajos:

```python
temperature=0
```

generan respuestas más:
- consistentes
- determinísticas
- predecibles

Esto es especialmente útil:
- en testing
- validaciones
- workflows estructurados
- agentes que requieren comportamientos repetibles

---

## Tu misión

Continuarás trabajando sobre el agente del Quest 03.

El laboratorio ya incluye un archivo compartido para las leyes del sistema:

```text
common/prompts/system_prompt.py
```

Dentro encontrarás una variable llamada:

```python
system_prompt
```

Tu tarea será modificarla y utilizarla dentro del agente.

---

### Deberás:

1. abrir:

```text
common/prompts/system_prompt.py
```

2. modificar el contenido de `system_prompt`
3. importar el prompt desde tu aplicación principal
4. usar `GenerateContentConfig`
5. enviar el `system_instruction`
6. configurar `temperature=0`

---

## Resultado esperado

Sin importar lo que escriba el usuario, el agente debería obedecer las leyes del sistema.

Ejemplo:

```text
🧑 Tú >
¿Cuál es la capital de Francia?

🤖 Agente >
EL LABORATORIO ESCUCHA.
```

---

## Ejecutar el Quest

```bash
uv run python -m quests.quest_04_laws_of_arkanum.starter.main \
"¿Cuál es la capital de Francia?"
```

---

## Criterio de éxito

Completaste el Quest si:

- el agente utiliza un `system_prompt`
- el comportamiento cambia correctamente
- las respuestas son consistentes
- el modelo obedece las instrucciones del sistema

---