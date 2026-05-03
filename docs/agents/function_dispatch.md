# Function Dispatch

> *“El agente expresa una intención.  
> El programa decide cómo convertirla en acción.”*  
> — Zhyréon

El modelo no ejecuta funciones directamente.

Cuando usa function calling, normalmente produce algo como:

```text
write_file({"file_path": "notes.txt", "content": "Hola"})
```

Eso representa una intención.

Tu programa debe convertir esa intención en una llamada real de Python.

---

## El problema

Supongamos que el modelo solicita esta función:

```python
function_name = "write_file"
```

Ese valor es texto.

Pero para ejecutar código necesitamos llamar una función real:

```python
write_file(...)
```

Ahí entra el function dispatch.

---

## Function map

Un `function_map` es un diccionario que conecta nombres de funciones con funciones reales.

```python
function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}
```

Esto significa:

```text
"write_file" → write_file
```

La clave es un string.

El valor es una función real de Python.

---

## Las funciones son objetos

En Python, las funciones pueden guardarse en variables.

```python
selected_function = write_file
```

Luego puedes ejecutarla:

```python
selected_function(...)
```

Por eso esto funciona:

```python
function_map[function_name]
```

Selecciona una función real usando el nombre solicitado por el modelo.

---

## Ejecutar la función seleccionada

Si:

```python
function_name = "write_file"
```

entonces:

```python
function_map[function_name]
```

equivale a:

```python
write_file
```

Y esto:

```python
function_map[function_name](...)
```

equivale a:

```python
write_file(...)
```

---

## Argumentos dinámicos

Los argumentos suelen venir en forma de diccionario:

```python
args = {
    "file_path": "notes.txt",
    "content": "Hola mundo",
}
```

Python permite pasar ese diccionario como argumentos nombrados usando:

```python
**args
```

Entonces:

```python
write_file(**args)
```

equivale a:

```python
write_file(
    file_path="notes.txt",
    content="Hola mundo",
)
```

---

## La línea completa

Esta línea:

```python
function_result = function_map[function_name](**args)
```

significa:

1. busca la función en `function_map`
2. selecciónala usando `function_name`
3. ejecuta esa función
4. pásale los argumentos contenidos en `args`
5. guarda el resultado en `function_result`

---

### ¿Por qué validar el nombre?

El modelo podría pedir una función inexistente.

Por eso conviene validar:

```python
if function_name not in function_map:
    ...
```

Esto evita intentar ejecutar algo desconocido.

---

### Inyectar argumentos protegidos

No todos los argumentos deberían venir del modelo.

Por ejemplo:

```python
working_directory
```

debería ser controlado por el programa, no por el LLM.

Por eso podemos hacer:

```python
args["working_directory"] = "workspace"
```

antes de ejecutar la función.

Esto permite que el agente use herramientas sin controlar directamente los límites de seguridad.

---

## Idea importante

Function dispatch convierte una intención del modelo en una acción real del programa.

Ese es uno de los puentes centrales entre:

```text
LLM que razona
```

y:

```text
agente que actúa
```