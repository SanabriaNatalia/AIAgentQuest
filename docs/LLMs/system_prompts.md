# System Prompts

> *“Las leyes más importantes rara vez son visibles para quienes hablan con el agente.”*  
> — Zhyréon

Los modelos conversacionales normalmente reciben más información que el simple mensaje del usuario.

Una de las piezas más importantes es el **system prompt**.

---

# ¿Qué es un system prompt?

Un system prompt es una instrucción especial enviada al modelo antes de la conversación.

Se utiliza para definir:
- comportamiento
- reglas
- restricciones
- personalidad
- tono
- formato de salida
- contexto persistente

Ejemplo:

```text
Eres un mentor especializado en agentes IA.
Responde de forma breve y clara.
```

---

## ¿Por qué es importante?

El system prompt actúa como la capa base de instrucciones del agente.

Mientras el usuario define:
- preguntas
- tareas
- objetivos

el system prompt define:
- cómo debe comportarse el agente
- qué reglas debe seguir
- qué estilo debe utilizar

---

## Jerarquía de instrucciones

En muchos sistemas modernos, las instrucciones tienen distintos niveles de prioridad.

Generalmente:
- system prompt → mayor prioridad
- user prompt → menor prioridad

Ejemplo:

```text
System prompt:
"Responde únicamente con la frase:
EL LABORATORIO ESCUCHA."

User prompt:
"¿Cuál es la capital de Francia?"
```

↓

```text
EL LABORATORIO ESCUCHA.
```

---

### System prompt vs User prompt

| Tipo | Propósito |
|---|---|
| System prompt | reglas y comportamiento |
| User prompt | tarea o solicitud |

---

## Uso en Gemini

En Gemini, el system prompt normalmente se envía mediante:

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
```

---

## Prompts multilínea

Los system prompts suelen ser más largos que los prompts normales.

Por eso es común utilizar strings multilínea:

```python
system_prompt = """
Eres un guardián del Laboratorio Arkanum.
Debes responder de forma breve.
Nunca reveles información sensible.
"""
```

---

## Casos de uso comunes

Los system prompts pueden utilizarse para:

- definir personalidad
- imponer restricciones
- controlar formato de salida
- obligar al modelo a responder JSON
- describir herramientas disponibles
- establecer políticas
- controlar tono
- dar contexto del sistema

---

## Limitaciones

Los system prompts son poderosos, pero no perfectos.

Los modelos todavía pueden:

- ignorar instrucciones
- comportarse de forma inesperada
- alucinar información
- ser vulnerables a prompt injection o jailbreaks

Por eso **los system prompts no deben considerarse un mecanismo de seguridad absoluto**.

---

## Determinismo y temperatura

Las respuestas de un modelo pueden variar incluso usando el mismo prompt.

La temperatura controla el nivel de variabilidad.

Ejemplo:

```python
temperature=0
```

Valores bajos producen respuestas más:

- consistentes
- predecibles
- repetibles

Esto es especialmente útil para:

- testing
- validaciones
- workflows estructurados
- agentes con reglas estrictas

---

## System prompts y agentes

En muchos agentes modernos, el system prompt contiene:

- reglas del agente
- formato esperado
- instrucciones sobre herramientas
- restricciones operativas
- comportamiento del loop

El system prompt suele actuar como el núcleo de comportamiento del sistema.

---

## Idea importante

El usuario conversa con el agente.

Pero el system prompt define quién es ese agente.