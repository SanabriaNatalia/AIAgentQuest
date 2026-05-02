# Roles y Mensajes

> *“Una conversación no es una sola voz.  
> Es una secuencia de intenciones.”*  
> — Zhyréon

Los modelos conversacionales modernos trabajan con mensajes estructurados.

Cada mensaje representa una intervención dentro de una conversación y contiene información sobre:
- quién habla
- qué dice
- cómo debe interpretarse el contenido

En Gemini, OpenAI y muchos otros sistemas, las conversaciones se representan como listas de mensajes.

---

# ¿Por qué existen los roles?

Los roles permiten que el modelo comprenda el contexto conversacional.

No es lo mismo:

```text
user: Explica qué es un agente IA.
```

que:

```text
model: Explica qué es un agente IA.
```

El contenido puede ser idéntico, pero la intención cambia completamente.

Los roles ayudan al modelo a distinguir:
- instrucciones
- preguntas
- respuestas
- contexto
- comportamiento esperado

---

# Roles comunes

## `user`

Representa mensajes enviados por el usuario.

Ejemplo:

```python
types.Content(
    role="user",
    parts=[
        types.Part(
            text="¿Qué es un agente IA?"
        )
    ]
)
```

Normalmente contiene:
- preguntas
- instrucciones
- tareas
- contexto proporcionado por el usuario

---

## `model`

Representa respuestas generadas por el modelo.

Ejemplo:

```python
types.Content(
    role="model",
    parts=[
        types.Part(
            text="Un agente IA es un sistema capaz de..."
        )
    ]
)
```

Guardar respuestas del modelo permite construir historial conversacional y memoria contextual.

---

## `system`

Representa instrucciones globales sobre el comportamiento del modelo.

Normalmente se utiliza para definir:
- personalidad
- restricciones
- tono
- objetivos
- reglas del agente

Ejemplo conceptual:

```text
Eres un mentor arcano especializado en agentes IA.
Responde de forma breve y clara.
```

Dependiendo del SDK o proveedor, el rol `system` puede enviarse:
- como un mensaje adicional
- o mediante configuraciones separadas del modelo

---

# Conversaciones estructuradas

Una conversación completa suele representarse como una lista de mensajes:

```python
messages = [
    types.Content(
        role="user",
        parts=[
            types.Part(text="¿Qué es un agente IA?")
        ]
    ),

    types.Content(
        role="model",
        parts=[
            types.Part(
                text="Un agente IA es un sistema capaz de..."
            )
        ]
    ),

    types.Content(
        role="user",
        parts=[
            types.Part(
                text="Dame un ejemplo práctico."
            )
        ]
    ),
]
```

El modelo recibe toda esta estructura como contexto.

---

# `types.Content`

En Gemini, un mensaje se representa utilizando:

```python
types.Content
```

Este objeto contiene:
- el rol
- las partes del mensaje

Ejemplo:

```python
types.Content(
    role="user",
    parts=[
        types.Part(
            text="Hola"
        )
    ]
)
```

---

# `types.Part`

El contenido de un mensaje se divide en partes.

Una parte puede contener:
- texto
- imágenes
- audio
- archivos
- contenido multimodal

Ejemplo básico:

```python
types.Part(
    text="Hola"
)
```

Por eso incluso los mensajes simples utilizan:

```python
parts=[...]
```

en lugar de texto plano directamente.

---

# Contexto conversacional

Los modelos no “recuerdan” conversaciones automáticamente entre llamadas.

La aplicación debe reenviar el historial relevante en cada invocación.

Ejemplo:

```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=messages,
)
```

Mientras más mensajes se incluyan:
- más contexto recibe el modelo
- más coherente puede ser la conversación
- mayor será el consumo de tokens

### Context Pruning

A medida que una conversación crece, también crece la cantidad de contexto enviado al modelo.

Eso puede generar:
- mayor consumo de tokens
- respuestas más lentas
- pérdida de información importante dentro del contexto

Por eso muchos agentes implementan estrategias de *context pruning*.

La idea general es:
- conservar contexto relevante
- eliminar o resumir información menos importante

Algunas estrategias comunes incluyen:
- conservar solo los últimos mensajes
- resumir conversaciones antiguas
- filtrar mensajes irrelevantes
- recuperar contexto dinámicamente

Gestionar correctamente el contexto es una parte fundamental del diseño de agentes modernos.

---

# Memoria conversacional

La memoria en un agente normalmente consiste en:
- almacenar mensajes anteriores
- conservar contexto importante
- reenviar historial relevante

Esto permite que el modelo responda considerando interacciones previas.

---

# Idea clave

Un agente conversacional no funciona únicamente porque el modelo “sea inteligente”.

Funciona porque la aplicación:
- organiza mensajes
- conserva contexto
- estructura roles
- controla qué información recibe el modelo