# Quest 05 — El Directorio Prohibido

<p align="center">
    <img src="../../assets/images/quest-5-banner.png" alt="Quest 5 Banner" width="100%">
</p>

> *“Antes de entregar herramientas a un agente, traza los límites del mundo donde puede actuar.”*  
> — Zhyréon

## Información del Quest

|Acto| Dificultad | Tiempo estimado |
|---|---|---|
| II — Capacidad de Acción | 🟡 Intermedio | 15–25 mins |

---

## Objetivo

Un agente con herramientas puede ser poderoso.

Pero también puede ser peligroso.

Antes de permitirle leer archivos, escribir contenido o ejecutar código, necesitamos asegurarnos de que solo pueda actuar dentro de un directorio permitido.

En este Quest construiremos la frontera de seguridad del agente: su **working directory**.

---

## Qué aprenderás

- qué es un working directory
- por qué un agente necesita límites
- cómo evitar acceso a rutas no permitidas
- cómo validar rutas con `abspath`, `normpath` y `commonpath`
- por qué las herramientas (tools) deben devolver errores como texto

---

## ¿Por qué existe `workspace/`?

Seguramente ya viste la carpeta vacía :

```text
workspace/
```

en los Quests anteriores y te preguntaste:

> “¿Y esto para qué es?”

La respuesta es simple:

```text
workspace/
```

es el territorio permitido del agente.

Todo lo que el agente:
- lea
- escriba
- modifique
- ejecute

debería vivir dentro de ese espacio.

En agentes reales, este tipo de aislamiento es extremadamente importante.

Sin límites claros, un agente podría:
- acceder a archivos sensibles
- modificar contenido accidentalmente
- ejecutar código fuera de control
- comprometer el sistema donde está corriendo

Por eso muchos agentes modernos utilizan:
- sandboxes
- contenedores
- directorios restringidos
- entornos aislados

El `workspace/` del laboratorio es nuestra primera versión de esa idea.

---

## Las herramientas del agente

El laboratorio incluirá cuatro funciones base en:

```text
common/functions/
```

Estas funciones serán:

```text
get_files_info
get_file_content
write_file
run_python_file
```

Cada una representa una posible acción del agente sobre el sistema de archivos.

Pero antes de usarlas libremente, deben obedecer una regla:

> ninguna herramienta puede acceder a archivos por fuera del directorio permitido.

> Nota: Puedes abrir las funciones si lo deseas, allí encontrarás algunos TODOs, pero no corresponden a este quest. Los veremos más adelante.

## La idea clave

Las herramientas del agente recibirán rutas como argumentos.

Por ejemplo, una tool podría recibir:

```python
directory = "src"
```

o:

```python
file_path = "notes.txt"
```

Pero esas rutas deben interpretarse siempre como rutas relativas dentro del `working_directory`.

El agente puede pedir qué archivo o carpeta quiere revisar.

Nosotros definimos cuál es el territorio permitido.

```python
working_directory = "workspace"
```

Eso significa que el agente podrá explorar:

```text
workspace/
workspace/src/
workspace/notes.txt
```

pero no debería poder escapar hacia:

```text
../
../../
/home/user
/etc
```

---

### ¿Por qué importa?

Sin esta restricción, un agente con tools podría intentar leer o modificar archivos sensibles del computador.

Por ejemplo:

```text
../../secrets.txt
```

o:

```text
/home/user/.ssh/id_rsa
```

Incluso si el usuario no lo pidió maliciosamente, el modelo puede equivocarse.

Por eso las tools deben tener [guardrails](../../docs/agents/guardrails.md).


## La frontera del agente

Usaremos un `working_directory` como frontera segura.

### Cómo validar la frontera

La función que debes completar en este quest está en:

```text
common/functions/get_valid_target_path.py
```

Esta función recibirá:

```python
working_directory
```

y:

```python
target_path
```

**Tu trabajo será construir una ruta segura.**

### Validación de rutas

Para poder ejecutar esta validación, es necesario obtener primero la ruta absoluta del directorio de trabajo (working directory). Esto nos da una referencia absoluta del territorio permitido.

```python
working_dir_abs = os.path.abspath(working_directory)
```

Luego debemos compararla con la ruta final solicitada (la del archivo que vamos a leer, escribir o ejecutar):

```python
target_path = os.path.normpath(
    os.path.join(working_dir_abs, path)
)
```

Finalmente, debemos validar que la ruta final siga dentro del directorio permitido:

```python
os.path.commonpath([working_dir_abs, target_path]) == working_dir_abs
```

Si esta condición es falsa, la herramienta debe bloquear la acción.

---

## Errores como observaciones

Cuando una herramienta falla, no queremos que todo el agente explote.

Queremos que la herramienta devuelva una [observación textual](../../docs/agents/error_handling.md).

Ejemplo:

```python
try:
    ...
except Exception as e:
    return f"Error: {e}"
```

Esto es importante porque el agente necesita poder leer el error y decidir qué hacer después.

---

## Resultado esperado

Una llamada válida debería funcionar:

```text
get_files_info("./workspace", ".")
```

Una llamada inválida debería bloquearse:

```text
get_files_info("./workspace", "../")
```

Resultado esperado:

```text
Error: Cannot list '../' as it is outside the permitted working directory
```

## Tu misión

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

```
quests/quest_05_forbidden_directory/starter/main.py
```

Este archivo ejecuta casos de prueba manuales para validar rutas permitidas y prohibidas.

Tu tarea será completar los bloques `try/except` para que:

* las rutas permitidas muestren PASS
* las rutas prohibidas también muestren PASS cuando sean bloqueadas correctamente
* cualquier comportamiento inesperado muestre FAIL

---

## Pista

La validación principal debería verse parecida a esto:

```python
os.path.commonpath([working_dir_abs, resolved_target_path]) == working_dir_abs
```

No copies la línea sin entenderla.

Léela así:

> “La ruta común entre el territorio permitido y la ruta solicitada debe seguir siendo el territorio permitido.”

---

## Criterio de éxito

Completaste el Quest si:

- las tools funcionan dentro del `working_directory`
- las tools bloquean rutas externas
- los errores se devuelven como texto
- el agente no puede escapar del directorio permitido

### Validación de rutas

Para implementar la frontera del agente necesitarás trabajar con:

- [`os.path.abspath()`](https://docs.python.org/es/3/library/os.path.html#os.path.abspath)
- [`os.path.join()`](https://docs.python.org/es/3/library/os.path.html#os.path.join)
- [`os.path.normpath()`](https://docs.python.org/es/3/library/os.path.html#os.path.normpath)
- [`os.path.commonpath()`](https://docs.python.org/es/3/library/os.path.html#os.path.commonpath)

Hacer click en los enlaces te llevará a la documentación oficial.
También puedes consultar en [esta entrada del códice](../../docs/security/path_validation.md).
