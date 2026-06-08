# Quest 04 — Las Leyes del Arkanum

<p align="center">
    <img src="../../assets/images/quest-4-banner.png" alt="Quest 4 Banner" width="100%">
</p>

## 🎭 Lore

> *“Todo agente obedece primero las leyes que le dieron forma.”*
>
> — Zhyréon

## Información del Quest

| Acto | Dificultad | Tiempo estimado |
|---|---|---|
| I — Fundamentos del Agente | 🟢 Fácil | 10–15 mins |

---

## 🎯 Objetivo

Controlar el comportamiento del agente usando un **system prompt**: una capa de instrucciones internas que define cómo debe comportarse, independientemente de lo que diga el usuario.

Hasta ahora el agente solo respondía directamente a lo que el usuario escribía. Los agentes modernos suelen tener una capa adicional de reglas internas; eso es lo que construirás aquí.

---

## 📚 Conceptos clave

### Qué aprenderás

- qué es un system prompt
- diferencia entre instrucciones del sistema y prompts del usuario
- cómo controlar el comportamiento del modelo
- cómo usar `GenerateContentConfig`
- cómo crear respuestas más determinísticas usando `temperature`

### ¿Qué es un system prompt?

El [system prompt](../../docs/LLMs/system_prompts.md) es una instrucción especial enviada al modelo antes de la conversación.

Se usa para:
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

### Prioridad de instrucciones

En muchos modelos conversacionales, las instrucciones del sistema tienen mayor prioridad que los prompts del usuario.

```text
System prompt:
"Responde únicamente: LAS LEYES DEL ARKANUM SON ABSOLUTAS."

User prompt:
"¿Cuál es la capital de Francia?"
```

↓

```text
"LAS LEYES DEL ARKANUM SON ABSOLUTAS."
```

### Configuración del modelo

En Gemini, el system prompt se envía usando:

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

### Temperatura

Los modelos de lenguaje no siempre producen exactamente la misma respuesta. La [temperatura](../../docs/LLMs/temperature.md) controla el nivel de variabilidad.

Valores bajos:

```python
temperature=0
```

generan respuestas más:
- consistentes
- determinísticas
- predecibles

Útil en testing, validaciones, workflows estructurados, y agentes que requieren comportamientos repetibles.

---

## 📋 Tu misión

Continúa trabajando sobre el agente del Quest 03.

El laboratorio ya incluye un archivo compartido para las leyes del sistema:

```text
common/prompts/system_prompt.py
```

Dentro encontrarás una variable llamada `system_prompt`. Tu tarea será modificarla y usarla dentro del agente.

1. abrir `common/prompts/system_prompt.py` y modificar el contenido de `system_prompt`
2. importar el prompt desde tu aplicación principal
3. usar `GenerateContentConfig`
4. enviar el `system_instruction`
5. configurar `temperature=0`

---

## ✅ Resultado esperado

Sin importar lo que escriba el usuario, el agente debería obedecer las leyes del sistema.

```text
🧑 Prompt: ¿Cuál es la capital de Francia?

Prompt tokens: 42
Response tokens: 14

🤖 Agente: LAS LEYES DEL ARKANUM SON ABSOLUTAS.
```

---

## 🔗 Referencias

- [System prompts](../../docs/LLMs/system_prompts.md)
- [Temperatura](../../docs/LLMs/temperature.md)
