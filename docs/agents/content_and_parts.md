# Content y Parts

> *“Una respuesta no siempre es una sola cosa.”*  
> — Zhyréon

En Gemini, las respuestas no se representan como un único bloque de texto.

En cambio, utilizan una estructura más flexible:

```text
Content
└── parts[]
```

---

## ¿Qué es Content?

`Content` representa un mensaje completo dentro de la conversación.

### Ejemplo conceptual:

```python
types.Content(
    role="user",
    parts=[...]
)
```

o:

```python
types.Content(
    role="tool",
    parts=[...]
)
```

Un `Content` puede pertenecer a:
- usuario
- modelo
- herramienta

---

## ¿Qué es Part?

Una `Part` representa una pieza individual dentro del mensaje.

Ejemplos de parts:
- texto
- imágenes
- function calls
- function responses

### Ejemplo conceptual

```text
Content
├── Part(text)
├── Part(image)
└── Part(function_response)
```

Un solo mensaje puede contener múltiples tipos de contenido.

---

## Nuestro caso actual

En AI Agent Quest, nuestras tools devuelven:

```python
return types.Content(
    role="tool",
    parts=[
        types.Part.from_function_response(...)
    ]
)
```

Eso significa que:
- el mensaje contiene exactamente UNA parte
- esa parte es un `function_response`


### Entonces…

Cuando hacemos:

```python
part = function_call_result.parts[0]
```

estamos diciendo:

> “obtén la primera (y única) parte del mensaje.”

### ¿Por qué usamos [0]?

Porque actualmente nuestras tools siempre devuelven:

```text
parts = [
    una sola respuesta
]
```

Entonces:
- `parts[0]` existe
- representa la única respuesta importante
- no necesitamos iterar todavía


### ¿Qué contiene esa part?

La part contiene:

```python
part.function_response
```

y luego:

```python
part.function_response.response
```

Ejemplo:

```python
{
    "result": "Contenido del archivo..."
}
```

---

## Validaciones importantes

Por seguridad y claridad, validamos:

```python
if not function_call_result.parts:
```

para asegurarnos de que exista contenido.

Luego:

```python
if part.function_response is None:
```

para asegurarnos de que realmente sea una respuesta de tool.

Y finalmente:

```python
if part.function_response.response is None:
```

para validar que exista contenido real.

---

## ¿Por qué tantas validaciones?

Los modelos y APIs pueden:
- fallar
- responder parcialmente
- devolver estructuras inesperadas

En sistemas de agentes, es importante validar estructuras antes de asumir que existen.

---

## Más adelante...

En sistemas más avanzados, un `Content` puede contener múltiples parts:

```text
Content
├── texto
├── imagen
├── function_response
└── otra function_response
```

Pero por ahora:
- nuestras tools devuelven una sola part
- por eso usamos `parts[0]`

---

## Idea importante

`Content` representa un mensaje completo.

`Part` representa una pieza individual dentro de ese mensaje.

En este laboratorio todos los mensajes de function call que hemos creado devuelven una única parte.