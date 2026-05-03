# Quest 06 — El Cofre de Instrumentos

<p align="center">
    <img src="../../assets/images/quest-6-banner.png" alt="Quest 6 Banner" width="100%">
</p>

> *“Un agente deja de ser solo una voz cuando aprende a utilizar herramientas.”*  
> — Zhyréon

## Información del Quest

| Dificultad | Tiempo estimado |
|---|---|
| 🔴 Avanzado| 30 min - 1 h |

---

## Objetivo

Hasta ahora, nuestro agente solo podía conversar.

Pero los agentes modernos no solo generan texto.

También:
- leen archivos
- escriben contenido
- ejecutan código
- llaman APIs
- utilizan herramientas

En este Quest, el agente descubrirá sus primeros instrumentos.

Todavía no ejecutará herramientas.

Pero aprenderá:
- cuáles existen
- cómo describirlas
- cómo solicitar su uso

---

## Qué aprenderás

- qué es un `FunctionDeclaration`
- qué es un schema de herramienta
- cómo registrar tools en Gemini
- cómo describir funciones para un LLM
- qué son los `function_calls`
- diferencia entre:
  - texto generado
  - intención de usar una herramienta

---

## La idea clave

Los modelos NO ejecutan funciones directamente.

Un LLM no puede:
- correr Python
- abrir archivos
- usar tu terminal
- ejecutar código arbitrario

Lo que sí puede hacer es:

> describir qué herramienta quiere usar y con qué argumentos.

Tu programa sigue siendo quien:
- ejecuta funciones
- controla permisos
- valida inputs
- aplica [guardrails](../../docs/agents/guardrails.md)

---

## Cómo funciona el flujo

El proceso general se ve así:

1. Registramos herramientas disponibles
2. El usuario envía un prompt
3. El modelo decide qué herramienta usar
4. El modelo genera un function_call
5. Nuestro programa decide qué hacer


En este Quest llegaremos hasta el paso 4.

**Todavía no ejecutaremos funciones reales.**

---

## Function Declarations

Gemini utiliza:

```python
types.FunctionDeclaration
```

para describir herramientas disponibles para el modelo.

Estas declaraciones funcionan como schemas.

Le explican al LLM:
- nombre de la herramienta
- propósito
- parámetros esperados
- tipos de datos

---

## Ejemplo

El laboratorio ya incluye el schema de:

```python
get_files_info()
```

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

## Una observación importante

Probablemente notarás algo curioso:

```python
working_directory
```

NO aparece en el schema.

Eso es intencional.

El agente nunca debería controlar el `working_directory`.

Nosotros lo inyectamos desde afuera para mantener la seguridad del sistema.

---

## Registrando herramientas

Las funciones disponibles se registran usando:

```python
types.Tool
```

Ejemplo:

```python
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ]
)
```

En este Quest agregaremos todas las herramientas de las que disponemos.

---

## Agregando tools al modelo

Las tools se registran en:

```python
GenerateContentConfig
```

Ejemplo:

```python
config=types.GenerateContentConfig(
    tools=[available_functions],
    system_instruction=system_prompt,
)
```

---

## El system prompt del agente

Ahora que el agente conoce herramientas, debemos enseñarle cuándo usarlas.

Ejemplo:

```python
system_prompt = '''
Eres un agente de IA especializado en programación.
Cuando el usuario haga una pregunta o solicitud,
debes crear un plan de uso de herramientas.

Puedes realizar las siguientes operaciones:

- Listar archivos y directorios
- Leer contenido de archivos
- Escribir archivos
- Ejecutar archivos Python
'''
```

---

## Function Calls

Cuando el modelo decide usar una herramienta, Gemini genera:

```python
response.function_calls
```

Cada item contiene:
- nombre de la función
- argumentos sugeridos

Ejemplo conceptual:

```text
get_files_info({'directory': '.'})
```

---

## Tu misión

En este Quest trabajarás en cuatro partes.

---

### 1. Crear schemas faltantes

El laboratorio ya incluye:

```python
schema_get_files_info
```

Tu tarea será crear los schemas para:

```python
schema_get_file_content
schema_write_file
schema_run_python_file
```

Puedes guiarte del esquema que ya existe, pero si tienes dudas o quieres más información puedes consultar [esta entrada del Códice](../../docs/agents/tool_schemas.md).

---

### 2. Registrar herramientas

Debes completar:

```python
available_functions = types.Tool(
    function_declarations=[
        ...
    ]
)
```

registrando todas las herramientas del laboratorio.

---

### 3. Registrar las tools en Gemini

Debes agregar:

```python
tools=[available_functions]
```

dentro de:

```python
types.GenerateContentConfig(...)
```

para permitirle al agente el acceso a las herramientas.

---
### 4. Detectar function calls

Tu programa debe:

- revisar `response.function_calls`
- imprimir las funciones solicitadas por el modelo
- mostrar los argumentos sugeridos

Ejemplo esperado:

```text
Calling function:
get_files_info({'directory': '.'})
```

Si no existen function calls, el agente debe responder normalmente.

---

## Importante

En este Quest:

- NO ejecutaremos herramientas
- NO llamaremos funciones reales
- NO construiremos el agent loop todavía

Solo queremos comprobar que:

- el modelo conoce las herramientas
- el modelo sabe cuándo pedirlas

---

### 5. Actualizar el system prompt

Hasta ahora, el agente respondía únicamente:

```text
LAS LEYES DEL ARKANUM SON ABSOLUTAS.
```

Eso fue útil para aprender qué es un system prompt.

Pero ahora el agente necesita comportarse como un agente de herramientas.

Debes actualizar:

```text
common/prompts/system_prompt.py
```

para describir:

- qué herramientas existen
- cómo debe usarlas
- qué operaciones puede realizar

Usa el system_prompt del ejemplo más arriba.

---

## Importante

En este Quest:
- NO ejecutaremos herramientas
- NO llamaremos funciones reales
- NO construiremos el agent loop todavía

Solo queremos comprobar que:
- el modelo conoce las herramientas
- el modelo sabe cuándo pedirlas

---

## Resultado esperado

Prompt:

```text
what files are in the root?
```

Resultado esperado:

```text
Calling function:
get_files_info({'directory': '.'})
```

