# Validación de Rutas

> *“Un agente sin frontera no explora.  
> Invade.”*  
> — Zhyréon

Cuando un agente tiene herramientas para leer, escribir o ejecutar archivos, necesita límites claros.

La validación de rutas existe para asegurar que una herramienta solo pueda actuar dentro de un directorio permitido.

Ese directorio suele llamarse:

```text
working_directory
```

---

## El problema

Una herramienta puede recibir rutas como argumentos:

```python
"notes.txt"
```

```python
"src/app.py"
```

Pero también podría recibir rutas peligrosas:

```python
"../secrets.txt"
```

```python
"../../private/config.env"
```

```python
"/home/user/.ssh/id_rsa"
```

Sin validación, una herramienta podría acceder a archivos fuera del espacio permitido.

---

## La frontera

La regla es:

> toda ruta solicitada debe permanecer dentro del `working_directory`.

Por ejemplo:

```python
working_directory = "workspace"
```

Permitido:

```text
workspace/notes.txt
workspace/src/app.py
```

Bloqueado:

```text
../secrets.txt
../../private/config.env
/home/user/.ssh/id_rsa
```

---

## Las piezas de la frontera

Para proteger el `working_directory`, usaremos varias funciones de `os.path`.

---

### 1. `os.path.abspath()`

Convierte una ruta en una ruta absoluta.

```python
os.path.abspath("workspace")
```

Resultado aproximado:

```text
/home/user/ai-agent-quest/workspace
```

Esto nos da una referencia clara del territorio permitido.

---

### 2. `os.path.join()`

Une rutas.

```python
os.path.join(working_dir_abs, "src/app.py")
```

Resultado aproximado:

```text
/home/user/ai-agent-quest/workspace/src/app.py
```

Esto permite interpretar la ruta solicitada como una ruta relativa dentro del `working_directory`.

---

### 3. `os.path.normpath()`

Normaliza una ruta.

Esto es importante porque una ruta puede intentar escapar usando `..`.

```python
os.path.normpath("/home/user/project/workspace/../secrets.txt")
```

Resultado:

```text
/home/user/project/secrets.txt
```

Es decir:

```text
..
```

significa “sube una carpeta”.

---

### 4. `os.path.commonpath()`

Encuentra la ruta común entre dos rutas.

La usamos para verificar si la ruta final sigue dentro del `working_directory`.

```python
os.path.commonpath([working_dir_abs, resolved_target_path]) == working_dir_abs
```

Léelo así:

> “La ruta común entre el territorio permitido y la ruta solicitada debe seguir siendo el territorio permitido.”

Si esto es `True`, la ruta está dentro del territorio permitido.

Si esto es `False`, la ruta intenta escapar.

---

## Ejemplo válido

Supongamos:

```python
working_directory = "workspace"
target_path = "src/app.py"
```

Primero obtenemos la ruta absoluta:

```python
working_dir_abs = os.path.abspath(working_directory)
```

Resultado aproximado:

```text
/home/user/project/workspace
```

Luego construimos y normalizamos la ruta solicitada:

```python
resolved_target_path = os.path.normpath(
    os.path.join(working_dir_abs, target_path)
)
```

Resultado:

```text
/home/user/project/workspace/src/app.py
```

La ruta común entre ambas es:

```text
/home/user/project/workspace
```

✅ La ruta está dentro del `working_directory`.

---

## Ejemplo inválido

Supongamos:

```python
working_directory = "workspace"
target_path = "../secrets.txt"
```

Construimos y normalizamos la ruta:

```python
resolved_target_path = os.path.normpath(
    os.path.join(working_dir_abs, target_path)
)
```

Resultado aproximado:

```text
/home/user/project/secrets.txt
```

La ruta común entre:

```text
/home/user/project/workspace
```

y:

```text
/home/user/project/secrets.txt
```

es:

```text
/home/user/project
```

❌ La ruta común ya no es el `working_directory`.

La ruta intentó escapar.

---

## Función base

Una función reusable podría verse así:

```python
import os


def get_valid_target_path(
    working_directory: str,
    target_path: str,
) -> str:
    working_dir_abs = os.path.abspath(working_directory)

    resolved_target_path = os.path.normpath(
        os.path.join(working_dir_abs, target_path)
    )

    is_valid_path = (
        os.path.commonpath([working_dir_abs, resolved_target_path])
        == working_dir_abs
    )

    if not is_valid_path:
        raise RuntimeError(
            f"'{target_path}' is outside the permitted working directory"
        )

    return resolved_target_path
```

---

## Errores como texto

En herramientas para agentes, normalmente no queremos que una excepción rompa todo el programa.

Es común capturar errores y devolverlos como texto:

```python
try:
    ...
except Exception as e:
    return f"Error: {e}"
```

Esto permite que el agente reciba el error como una observación y pueda decidir qué hacer.

---

## Idea importante

La validación de rutas no es un detalle menor.

Es una frontera de seguridad.

Antes de permitir que un agente lea, escriba o ejecute archivos, debe existir una regla clara:

> ninguna herramienta puede actuar fuera del directorio permitido.