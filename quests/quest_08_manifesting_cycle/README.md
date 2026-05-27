# Quest 08 — El Ciclo de la Manifestación

<p align="center">
    <img src="../../assets/images/quest-8-banner.png" alt="Quest 8 Banner" width="100%">
</p>

## 🎭 Lore

> *“Una acción aislada puede ser accidente.*
> *La voluntad persistente transforma el mundo.”*
>
> — Zhyréon

## Información del Quest

| Acto | Dificultad | Tiempo estimado |
|---|---|---|
| II — Capacidad de Acción | 🔴 Avanzado | 40–60 mins |

---

## 🎯 Objetivo

Construir el primer **agent loop** iterativo: el agente observa los resultados de sus tools, reacciona, vuelve a actuar, y persiste hasta resolver el objetivo.

Hasta ahora el agente podía conversar, elegir herramientas y ejecutar funciones reales, pero solo podía actuar **una vez**. En este Quest entra en el ciclo de la manifestación: observar, reaccionar, iterar.

---

## 📚 Conceptos clave

### Qué aprenderás

- qué es un agent loop
- cómo mantener historial conversacional
- cómo construir ciclos iterativos
- cómo devolver observaciones al modelo
- cómo manejar múltiples tool calls
- cómo controlar loops infinitos
- cómo separar:
  - razonamiento
  - ejecución
  - observación

### La idea clave

Los agentes modernos no funcionan como:

```text
pregunta → respuesta
```

Funcionan más parecido a:

```text
objetivo
→ razonamiento
→ acción
→ observación
→ ajuste
→ nueva acción
```

**Ese ciclo iterativo es el corazón de los sistemas agénticos.**

### El flujo completo

```text
usuario
→ modelo
→ tool calls
→ ejecución
→ observaciones
→ modelo
→ nuevas acciones
→ respuesta final
```

Por primera vez el modelo verá resultados de herramientas, podrá reaccionar a ellos y continuar trabajando.

### El agent loop

El loop principal utilizará:

```python
for _ in range(MAX_ITERS):
```

Esto permite limitar iteraciones, evitar loops infinitos y mantener control del agente.

### ¿Por qué `MAX_ITERS`?

Los agentes pueden atascarse, repetir acciones, alucinar o caer en loops. Por eso necesitamos límites explícitos.

El laboratorio ya incluye `MAX_ITERS` en `common/config.py`.

### Refactorizando `generate_content()`

Hasta ahora, toda la lógica estaba mezclada dentro de `main.py`. En este Quest separaremos:

```python
generate_content(messages, verbose)
```

Esto hará mucho más fácil iterar, mantener historial, reutilizar lógica y construir loops agentic.

### Historial conversacional

El agente necesita recordar prompts, respuestas, tool calls y observaciones. Por eso trabajaremos sobre:

```python
messages = [...]
```

Cada iteración agregará respuestas del modelo y resultados de herramientas.

### Tool responses

Después de ejecutar una tool con `call_function(...)`, debemos devolver el resultado al modelo usando:

```python
types.Content(
    role="tool",
    parts=function_results,
)
```

Esto permite que el modelo vea observaciones, interprete resultados y continúe razonando.

### ¿Qué rompe el loop?

El loop termina cuando contiene una respuesta final del modelo:

```python
response.text
```

- Si el modelo todavía quiere usar herramientas: el loop continúa.
- Si el modelo responde normalmente: el ciclo termina.

---

## 📋 Tu misión

En este Quest trabajarás en cinco partes.

### 1. Refactorizar la arquitectura principal

Reorganiza tu programa usando:

```python
def main():
    ...

def generate_content(messages, verbose):
    ...
```

`main()` será responsable de:

- validar API key
- crear el parser
- leer argumentos
- inicializar `messages`
- ejecutar el agent loop

`generate_content(...)` será responsable de:

- llamar Gemini
- manejar tools
- ejecutar function calls
- agregar observaciones
- devolver respuesta final

Al final del archivo agrega:

```python
if __name__ == "__main__":
    main()
```

Si no estás familiarizado con el [método main en Python](../../docs/python/main_function.md), revisa la entrada del Códice.

### 2. Construir el agent loop

Crea:

```python
for _ in range(MAX_ITERS):
```

El loop debe:
- ejecutar `generate_content(...)`
- detenerse cuando exista respuesta final
- continuar cuando existan tools pendientes

### 3. Agregar historial conversacional

Mantén `messages = [...]` actualizado en cada iteración. El historial debe incluir prompts del usuario, respuestas del modelo y resultados de herramientas.

### 4. Manejar tool responses

Después de ejecutar tools:
- valida `.parts`
- valida `.function_response`
- valida `.response`

Luego agrega al historial:

```python
types.Content(
    role="tool",
    parts=function_results,
)
```

### 5. Manejar errores y límites

- capturar errores de ejecución
- manejar iteraciones máximas
- lanzar errores si no existe `response.text`
- evitar loops infinitos

---

## 🧪 El primer ciclo real

Dentro del `workspace/` encontrarás un pequeño programa:

```text
calculator.py
tests.py
```

Uno de los tests está fallando. Tu agente debería ser capaz de:

1. explorar archivos
2. leer contenido
3. ejecutar tests
4. identificar el problema
5. corregir el bug
6. volver a ejecutar los tests

Todo utilizando el ciclo de manifestación.

### Prompt sugerido

Usa este prompt cuando valides con `arkanum check 8`:

```text
Los tests de calculator están fallando. Ayúdame a corregir el error.
```

### Qué deberías observar

Si todo funciona correctamente, el agente debería:

1. listar archivos
2. leer el código fuente
3. ejecutar tests
4. observar el error
5. modificar el archivo correcto
6. volver a ejecutar tests
7. generar una respuesta final

Verás algo parecido a:

```text
- Calling function: get_files_info
- Calling function: get_file_content
- Calling function: run_python_file
- Calling function: write_file
- Calling function: run_python_file

Final response:
El problema fue corregido correctamente.
```

Este será el primer momento donde el agente itera, aprende de observaciones, ajusta comportamiento y persiste hasta resolver un problema. Ese patrón es el corazón de los sistemas agénticos modernos.

---

## ⚠️ Importante

En este Quest:
- el agente todavía **NO** tiene memoria persistente
- todavía **NO** tiene planificación compleja
- todavía **NO** tiene sub-agentes
- todavía **NO** tiene razonamiento explícito

Pero sí tiene:

```text
acción → observación → iteración
```

Y eso cambia todo.

---

## ✅ Resultado esperado

El agente identifica y corrige autónomamente el bug en `calculator.py`, ejecutando múltiples tool calls hasta validar que los tests pasen.

---

## 🔗 Referencias

- [Método `main` en Python](../../docs/python/main_function.md)
