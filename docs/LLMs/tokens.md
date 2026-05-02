# Tokens

> *“Toda invocación tiene un costo.  
> Incluso las palabras consumen energía.”*  
> — Zhyréon

Los modelos de lenguaje no procesan texto exactamente como los humanos.

En lugar de trabajar directamente con palabras o frases completas, utilizan pequeñas unidades llamadas **tokens**.

---

## ¿Qué es un token?

Un token es un fragmento de texto.

Dependiendo del modelo, un token puede representar:
- una palabra completa
- parte de una palabra
- puntuación
- espacios
- caracteres especiales

Por ejemplo:

```text
"Hola mundo"
```

podría dividirse internamente en varios tokens.

La cantidad exacta depende del modelo y su tokenizer.

---

## ¿Por qué importan los tokens?

Los tokens afectan:
- costo
- velocidad
- límites de contexto
- memoria conversacional

Mientras más tokens se envíen al modelo:
- más procesamiento requiere
- más costosa puede ser la invocación
- más tiempo puede tardar la respuesta

---

## Prompt tokens

Son los tokens enviados al modelo.

Incluyen:
- instrucciones
- historial conversacional
- system prompts
- contexto recuperado
- mensajes del usuario

En Gemini:

```python
usage.prompt_token_count
```

---

## Response tokens

Son los tokens generados por el modelo como respuesta.

En Gemini:

```python
usage.candidates_token_count
```

---

## Usage metadata

Muchos proveedores de LLMs incluyen metadata sobre consumo de tokens.

En Gemini:

```python
response.usage_metadata
```

Ejemplo:

```python
usage = response.usage_metadata

print(usage.prompt_token_count)
print(usage.candidates_token_count)
```

---

## Context window

Los modelos tienen un límite máximo de tokens que pueden procesar en una sola conversación.

Ese límite se conoce como:

```text
context window
```

Todo lo enviado al modelo comparte ese espacio:
- system prompts
- historial
- documentos
- tools
- respuestas

Si el contexto crece demasiado:
- algunos mensajes podrían descartarse
- el modelo puede perder coherencia
- aumenta el costo de procesamiento

---

## Tokens y memoria

La memoria conversacional normalmente funciona reenviando mensajes anteriores.

Eso significa que mientras más larga sea la conversación:
- más tokens se consumen
- más contexto recibe el modelo

Por eso los agentes modernos suelen gestionar cuidadosamente qué información conservar.

### Context pruning

A medida que una conversación crece, también crece la cantidad de tokens enviados al modelo.

Muchos agentes implementan estrategias de *context pruning* para controlar el tamaño del contexto.

La idea general es:
- conservar información importante
- resumir conversaciones antiguas
- eliminar contexto irrelevante
- recuperar información dinámicamente

Gestionar correctamente el contexto es una parte importante del diseño de agentes.

---

## Tokens y herramientas

Cuando un agente utiliza herramientas, los resultados también consumen tokens.

Por ejemplo:
- archivos
- logs
- respuestas de APIs
- resultados de búsquedas
- documentos recuperados

Todo eso puede formar parte del contexto enviado al modelo.

---

## Idea importante

Los modelos no “ven” conversaciones como humanos.

Ven secuencias de tokens.

Comprender cómo crece el contexto y cómo se consumen tokens es fundamental para construir:
- agentes eficientes
- sistemas escalables
- memoria conversacional
- pipelines RAG
- workflows complejos