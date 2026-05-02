# ¿Qué es un LLM?

> *“Las grandes inteligencias no nacen comprendiendo el mundo.  
> Aprenden observando patrones dentro del lenguaje.”*  
> — Zhyréon

LLM significa:

```text
Large Language Model
```

o:

```text
Modelo de Lenguaje Grande
```

Son sistemas entrenados para procesar y generar lenguaje natural.

Herramientas como:
- ChatGPT
- Gemini
- Claude
- Cursor
- Copilot

están impulsadas por LLMs.

---

## ¿Qué hace un LLM?

Un LLM recibe texto como entrada y genera texto como salida.

Por ejemplo:

```text
Prompt:
"¿Qué es un agente IA?"
```

↓

```text
Respuesta:
"Un agente IA es un sistema capaz de..."
```

Desde fuera parece una conversación.

Internamente, el modelo está realizando predicción de tokens.

---

## Predicción de tokens

La idea central de un LLM es sorprendentemente simple:

> predecir qué token debería venir después.

Por ejemplo:

```text
"La capital de Francia es..."
```

El modelo considera múltiples posibilidades y estima cuál es la continuación más probable.

En este caso:

```text
"París"
```

---

## ¿Por qué parecen inteligentes?

Porque fueron entrenados con cantidades masivas de texto:
- libros
- documentación
- artículos
- código
- conversaciones
- sitios web

Durante el entrenamiento aprenden:
- patrones del lenguaje
- relaciones entre conceptos
- estructuras de razonamiento
- estilos de escritura
- correlaciones estadísticas

Eso les permite producir respuestas que parecen coherentes e incluso razonadas.

---

## ¿Qué significa “Large”?

El término “large” normalmente hace referencia a:
- la cantidad de parámetros
- la cantidad de datos utilizados en entrenamiento
- la escala computacional del modelo

Los modelos modernos suelen contener:
- miles de millones
- o incluso billones de parámetros

---

## Tokens y contexto

Los LLMs no trabajan directamente con palabras completas.

Procesan secuencias de [tokens](tokens.md).

El modelo recibe:
- instrucciones
- historial
- documentos
- prompts
- mensajes

Todo convertido en tokens.

---

# Context window

Los modelos tienen un límite máximo de contexto que pueden procesar en una sola invocación.

Ese límite se conoce como:

```text
context window
```

Todo lo enviado al modelo comparte ese espacio:
- system prompts
- historial conversacional
- herramientas
- archivos
- respuestas previas

---

## Lo que un LLM NO es

Un LLM no:
- “piensa” como un humano
- comprende conscientemente el mundo
- posee memoria persistente real
- ejecuta acciones por sí mismo

Por sí solo, un LLM normalmente:
- recibe contexto
- genera texto
- devuelve una respuesta

---

## Entonces… ¿qué es un agente?

Un agente utiliza un LLM como núcleo de razonamiento, pero agrega capacidades adicionales como:
- memoria
- herramientas
- workflows
- planificación
- ejecución de acciones

Por eso:
- un chatbot simple no necesariamente es un agente
- pero un sistema capaz de actuar sobre herramientas sí puede convertirse en uno

---

## Idea importante

Un LLM es el motor conversacional.

Un agente es el sistema construido alrededor de ese motor.