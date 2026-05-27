# Quest 05 — El Directorio Prohibido

<p align="center">
    <img src="../../assets/images/quest-5-banner.png" alt="Quest 5 Banner" width="100%">
</p>

## 🎭 Lore

> *“Antes de entregar herramientas a un agente, traza los límites del mundo donde puede actuar.”*
>
> — Zhyréon

## Información del Quest

| Acto | Dificultad | Tiempo estimado |
|---|---|---|
| II — Capacidad de Acción | 🟡 Intermedio | 15–25 mins |

---

## 🎯 Objetivo

Construir la **frontera de seguridad** del agente: un `working_directory` permitido y una función que valide rutas para impedir que el agente lea, escriba o ejecute fuera de ese territorio.

Un agente con herramientas puede ser poderoso, pero también peligroso. Antes de darle acceso a archivos, necesitamos asegurarnos de que solo pueda actuar dentro de un directorio permitido.

---

## 📚 Conceptos clave

### Qué aprenderás

- qué es un working directory
- por qué un agente necesita límites
- cómo evitar acceso a rutas no permitidas
- cómo validar rutas con `abspath`, `normpath` y `commonpath`
- por qué las herramientas (tools) deben devolver errores como texto

### ¿Por qué existe `workspace/`?

La carpeta `workspace/` que viste vacía en quests anteriores es el **territorio permitido del agente**. Todo lo que el agente lea, escriba, modifique o ejecute debería vivir dentro de ese espacio.

En agentes reales este aislamiento es extremadamente importante. Sin límites claros, un agente podría:
- acceder a archivos sensibles
- modificar contenido accidentalmente
- ejecutar código fuera de control
- comprometer el sistema donde está corriendo

Por eso muchos agentes modernos utilizan sandboxes, contenedores, directorios restringidos o entornos aislados. El `workspace/` del laboratorio es nuestra primera versión de esa idea.

### Las herramientas del agente

El laboratorio incluirá cuatro funciones base en `common/functions/`:

```text
get_files_info
get_file_content
write_file
run_python_file
```

Cada una representa una posible acción del agente sobre el sistema de archivos. Pero antes de usarlas libremente, deben obedecer una regla:

> ninguna herramienta puede acceder a archivos por fuera del directorio permitido.

> Nota: puedes abrir las funciones si lo deseas; allí encontrarás TODOs, pero no corresponden a este quest. Los veremos más adelante.

### La idea clave

Las herramientas del agente recibirán rutas como argumentos:

```python
directory = "src"
file_path = "notes.txt"
```

Esas rutas deben interpretarse siempre como rutas **relativas** dentro del `working_directory`. El agente puede pedir qué archivo o carpeta quiere revisar; nosotros definimos cuál es el territorio permitido:

```python
working_directory = "workspace"
```

El agente podrá explorar:

```text
workspace/
workspace/src/
workspace/notes.txt
```

pero no debería escapar hacia:

```text
../
../../
/home/user
/etc
```

### ¿Por qué importa?

Sin esta restricción, un agente con tools podría intentar leer o modificar archivos sensibles:

```text
../../secrets.txt
/home/user/.ssh/id_rsa
```

Incluso si el usuario no lo pidió maliciosamente, el modelo puede equivocarse. Por eso las tools deben tener [guardrails](../../docs/agents/guardrails.md).

### Cómo validar la frontera

Primero obtener la ruta absoluta del directorio de trabajo (referencia absoluta del territorio permitido):

```python
working_dir_abs = os.path.abspath(working_directory)
```

Luego comparar con la ruta final solicitada:

```python
target_path = os.path.normpath(
    os.path.join(working_dir_abs, path)
)
```

Finalmente, validar que la ruta final siga dentro del directorio permitido:

```python
os.path.commonpath([working_dir_abs, target_path]) == working_dir_abs
```

Si esa condición es falsa, la herramienta debe bloquear la acción.

### Errores como observaciones

Cuando una herramienta falla, no queremos que todo el agente explote. Queremos que la herramienta devuelva una [observación textual](../../docs/agents/error_handling.md):

```python
try:
    ...
except Exception as e:
    return f"Error: {e}"
```

El agente necesita poder leer el error y decidir qué hacer después.

### Validación de rutas — funciones

Necesitarás trabajar con:

- [`os.path.abspath()`](https://docs.python.org/es/3/library/os.path.html#os.path.abspath)
- [`os.path.join()`](https://docs.python.org/es/3/library/os.path.html#os.path.join)
- [`os.path.normpath()`](https://docs.python.org/es/3/library/os.path.html#os.path.normpath)
- [`os.path.commonpath()`](https://docs.python.org/es/3/library/os.path.html#os.path.commonpath)

---

## 📋 Tu misión

En este quest trabajarás en dos archivos.

### 1. Completar la frontera del agente

Debes completar:

```text
common/functions/get_valid_target_path.py
```

La función debe:

1. convertir `working_directory` en ruta absoluta
2. unir esa ruta con `target_path`
3. normalizar la ruta resultante
4. validar que siga dentro del `working_directory`
5. lanzar `RuntimeError` si intenta escapar
6. retornar la ruta validada si es segura

### 2. Completar el runner de pruebas

También debes completar:

```text
quests/quest_05_forbidden_directory/starter/main.py
```

Este archivo ejecuta casos de prueba manuales para validar rutas permitidas y prohibidas.

Tu tarea será completar los bloques `try/except` para que:

- las rutas permitidas muestren PASS
- las rutas prohibidas también muestren PASS cuando sean bloqueadas correctamente
- cualquier comportamiento inesperado muestre FAIL

---

## ✅ Resultado esperado

Una llamada válida debería funcionar:

```text
get_files_info("./workspace", ".")
```

Una llamada inválida debería bloquearse:

```text
get_files_info("./workspace", "../")
```

Resultado:

```text
Error: Cannot list '../' as it is outside the permitted working directory
```

---

## 🔗 Referencias

- [Guardrails](../../docs/agents/guardrails.md)
- [Error handling](../../docs/agents/error_handling.md)
- [Path validation — entrada del códice](../../docs/security/path_validation.md)
- [`os.path.abspath()`](https://docs.python.org/es/3/library/os.path.html#os.path.abspath)
- [`os.path.join()`](https://docs.python.org/es/3/library/os.path.html#os.path.join)
- [`os.path.normpath()`](https://docs.python.org/es/3/library/os.path.html#os.path.normpath)
- [`os.path.commonpath()`](https://docs.python.org/es/3/library/os.path.html#os.path.commonpath)
