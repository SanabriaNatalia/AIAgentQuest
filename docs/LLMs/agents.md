# ¿Qué es un Agente?

> *“Un modelo responde.  
> Un agente actúa.”*  
> — Zhyréon

Un agente es un sistema capaz de:
- interpretar objetivos
- tomar decisiones
- utilizar herramientas
- mantener contexto
- ejecutar acciones

Muchos agentes modernos utilizan un LLM como núcleo de razonamiento.

Sin embargo, un agente es más que un modelo generando texto.

---

## LLM vs Agente

Un LLM normalmente:
- recibe contexto
- genera texto
- devuelve una respuesta

Un agente agrega capacidades adicionales alrededor del modelo.

---

### LLM

```text
Input → Modelo → Respuesta
```

Ejemplo:

```text
Pregunta:
"¿Qué es Python?"

Respuesta:
"Python es un lenguaje de programación..."
```


### Agente

```text
Objetivo
↓
Razonamiento
↓
Selección de herramientas
↓
Acciones
↓
Nuevo contexto
↓
Más razonamiento
```

El agente puede ejecutar múltiples pasos antes de responder.

---

## ¿Qué puede hacer un agente?

Dependiendo de sus herramientas y diseño, un agente puede:

- leer archivos
- escribir código
- buscar información
- ejecutar comandos
- llamar APIs
- consultar bases de datos
- analizar documentos
- coordinar otros agentes

---

## Herramientas

Las herramientas son una parte fundamental de los agentes modernos.

Por ejemplo:

```text
- read_file()
- write_file()
- search_web()
- execute_python()
```

El agente decide:
- cuándo utilizarlas
- con qué argumentos
- en qué orden

---

## Memoria y contexto

Muchos agentes mantienen historial conversacional o estado interno.

Eso les permite:
- recordar instrucciones
- continuar tareas largas
- conservar contexto relevante
- actuar de manera más coherente

La memoria normalmente se implementa:
- almacenando mensajes
- reenviando contexto
- recuperando información relevante

---

## Loops de razonamiento

Muchos agentes funcionan mediante ciclos iterativos.

Ejemplo conceptual:

```text
1. Recibir objetivo
2. Analizar situación
3. Elegir acción
4. Ejecutar herramienta
5. Observar resultado
6. Repetir
```

Esto permite resolver tareas complejas paso a paso.

---

## Agentes modernos

Herramientas como:
- Claude Code
- Cursor
- Devin
- OpenCode
- Copilot Workspace

utilizan arquitecturas basadas en agentes.

Aunque los detalles internos varían, muchos comparten ideas similares:
- uso de herramientas
- memoria contextual
- loops de razonamiento
- planificación
- ejecución iterativa

---

## ¿Un chatbot es un agente?

No necesariamente.

Un chatbot simple puede limitarse a:
- recibir mensajes
- generar respuestas

Sin ejecutar acciones reales.

Un sistema suele empezar a considerarse agente cuando puede:
- actuar sobre herramientas
- modificar el entorno
- tomar decisiones dentro de un workflow

---

## Arquitectura básica de un agente

Un agente moderno suele incluir:

| Componente | Función |
|---|---|
| LLM | razonamiento y generación |
| Memoria | contexto conversacional |
| Herramientas | interacción con sistemas externos |
| Planner / Loop | control de ejecución |
| Estado | seguimiento de objetivos y tareas |

---

## Idea importante

El modelo no es el agente.

El modelo es solo una parte del sistema.

El agente emerge de la combinación entre:
- razonamiento
- memoria
- contexto
- herramientas
- ejecución