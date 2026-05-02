# Error Handling

> *“Un error que el agente puede leer no es un fracaso.  
> Es una observación.”*  
> — Zhyréon

Cuando una herramienta falla, tenemos dos opciones:

1. romper el programa
2. devolver información útil al agente

En sistemas basados en agentes, normalmente queremos la segunda opción.

---

## El problema

Supongamos que una tool intenta leer un archivo que no existe:

```python
open("missing.txt")
```

Python lanzará una excepción:

```text
FileNotFoundError
```

Si esa excepción no se maneja correctamente, el agente completo puede detenerse.

---

### ¿Por qué esto es un problema?

Un agente moderno normalmente:
- usa múltiples herramientas
- ejecuta pasos iterativos
- toma decisiones usando observaciones del entorno

Si una tool rompe completamente el programa:
- el loop del agente termina
- el modelo pierde contexto
- el agente no puede recuperarse

---

## La idea clave

Las tools de un agente deberían:
- capturar errores
- convertirlos en texto
- devolver observaciones útiles

---

## Ejemplo básico

### ❌ Sin manejo de errores

```python
def read_file(path):
    with open(path, "r") as file:
        return file.read()
```

Si el archivo no existe:

```text
FileNotFoundError
```

El programa puede explotar.

### ✅ Con manejo de errores

```python
def read_file(path):
    try:
        with open(path, "r") as file:
            return file.read()

    except Exception as e:
        return f"Error: {e}"
```

Ahora la tool siempre devuelve un string.

### ¿Por qué devolver texto?

Porque el agente necesita poder leer lo que ocurrió.

Por ejemplo:

```text
Error: File not found
```

puede convertirse en una observación útil para el modelo.

El agente podría:
- intentar otra ruta
- corregir el nombre
- preguntar al usuario
- usar otra herramienta

---

## Errors as observations

En muchos agentes modernos:
- respuestas de tools
- resultados de APIs
- errores
- logs

son tratados como observaciones del entorno.

El modelo recibe esa información y decide qué hacer después.

---

## Consistencia de retorno

Una práctica común es que las tools siempre retornen el mismo tipo de dato.

Por ejemplo:

```python
str
```

Incluso cuando algo falla.

### Ejemplo práctico

```python
def get_file_content(path):
    try:
        with open(path, "r") as file:
            return file.read()

    except Exception as e:
        return f"Error: {e}"
```

Resultado exitoso:

```text
Hello world
```

Resultado con error:

```text
Error: [Errno 2] No such file or directory
```

En ambos casos:
- la tool devuelve un string
- el agente sigue funcionando

---

## ¿Debemos capturar todas las excepciones?

En herramientas para agentes pequeños o educativos, normalmente sí.

Por simplicidad:

```python
except Exception as e:
```

En sistemas más grandes, es común manejar excepciones específicas.

Por ejemplo:

```python
except FileNotFoundError:
```

o:

```python
except PermissionError:
```

---

## Manejo de errores y agentes

El manejo de errores es especialmente importante cuando un agente:
- ejecuta código
- usa filesystem
- llama APIs
- usa herramientas externas
- opera de forma autónoma

Los errores no deben destruir el loop del agente.

Deben convertirse en información útil.

---

## Idea importante

Una excepción destruye ejecución.

Una observación permite razonamiento.