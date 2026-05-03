# Tool Schemas

> *“Un agente no puede usar una herramienta que no comprende.”*  
> — Zhyréon

Los modelos de lenguaje no conocen automáticamente las funciones de tu programa.

Antes de que un agente pueda solicitar una herramienta, primero debemos describirla.

Esa descripción se realiza mediante un schema.

---

## ¿Qué es un schema?

Un schema es una descripción estructurada de una herramienta.

Le explica al modelo:
- cómo se llama la función
- qué hace
- qué parámetros recibe
- qué tipo de datos espera

En Gemini, esto se construye usando:

```python
types.FunctionDeclaration
```

**El modelo NO ejecuta funciones directamente.**

El schema solo le enseña:

> **“esta herramienta existe y así se utiliza”.**

Luego, el modelo puede generar algo como:

```text
get_files_info({'directory': '.'})
```

Tu programa sigue siendo quien decide:
- si ejecutar la función
- cuándo ejecutarla
- con qué permisos

---

## Estructura básica

Ejemplo:

```python
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path relative to the working directory",
            ),
        },
    ),
)
```

---

## Partes importantes

### Nombre

```python
name="get_files_info"
```

Debe coincidir con el nombre real de la función.


### Descripción

```python
description="Lists files in a specified directory..."
```

Explica qué hace la herramienta.

Mientras más clara sea la descripción:
- mejor entenderá el modelo cuándo usarla
- mejores serán los function calls

### Parameters

```python
parameters=types.Schema(...)
```

Describe los argumentos esperados.

---

### Tipos de datos

Gemini usa:

```python
types.Type
```

Algunos tipos comunes:

| Tipo | Uso |
|---|---|
| `STRING` | texto |
| `INTEGER` | enteros |
| `NUMBER` | números decimales |
| `BOOLEAN` | true / false |
| `OBJECT` | diccionarios |
| `ARRAY` | listas |

---

### Properties

Dentro de:

```python
properties={}
```

describimos cada parámetro individual.

Ejemplo:

```python
"directory": types.Schema(
    type=types.Type.STRING,
    description="Directory path relative to the working directory",
)
```

---

### ¿Por qué OBJECT?

La mayoría de function calls utilizan:

```python
type=types.Type.OBJECT
```

porque los argumentos suelen enviarse como diccionarios:

```python
{
    "directory": "."
}
```

---

### Parámetros ocultos

A veces una función real tiene parámetros que NO queremos mostrarle al modelo.

Ejemplo:

```python
def get_files_info(working_directory, directory="."):
```

El modelo NO debería controlar:

```python
working_directory
```

Por eso ese parámetro NO aparece en el schema.

Nosotros lo inyectamos manualmente desde afuera.

Esto es una forma de:
- encapsulación
- seguridad
- guardrail

---

## Required Fields

También es posible especificar parámetros obligatorios usando:

```python
required=[...]
```

Ejemplo:

```python
parameters=types.Schema(
    type=types.Type.OBJECT,
    properties={
        "file_path": types.Schema(
            type=types.Type.STRING,
            description="Relative path of the file to write",
        ),
        "content": types.Schema(
            type=types.Type.STRING,
            description="Content to write into the file",
        ),
    },
    required=["file_path", "content"], ## <- Acá le decimos cuáles parámetros debe utilizar sí o sí
)
```

Esto ayuda al modelo a entender qué argumentos son necesarios para utilizar correctamente la herramienta.

## Ejemplo completo

Supongamos esta función:

```python
def write_file(file_path, content):
```

Su schema podría verse así:

```python
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content into a file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Relative path of the file to write",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to write into the file",
            ),
        },
        required=["file_path", "content"],
    ),
)
```

---

# Registrando herramientas

Los schemas normalmente se registran usando:

```python
types.Tool
```

Ejemplo:

```python
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_write_file,
    ]
)
```

---

# Qué ocurre después

Una vez registradas las herramientas:
- el modelo puede verlas
- el modelo puede seleccionarlas
- el modelo puede generar `function_calls`

Pero:
- el modelo todavía NO ejecuta código
- tu programa sigue teniendo el control

---

# Idea importante

Un schema no ejecuta herramientas.

Un schema enseña herramientas.