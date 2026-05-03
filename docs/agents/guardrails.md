# Guardrails

> *“El poder de un agente no depende solo de lo que puede hacer.  
> También depende de lo que no se le permite hacer.”*  
> — Zhyréon

Los guardrails son restricciones, validaciones y mecanismos de protección que limitan el comportamiento de un sistema basado en IA.

La idea viene de las barreras metálicas en carreteras:

> no impiden avanzar,  
> pero sí evitan que el vehículo se salga del camino.

En agentes IA, los guardrails cumplen exactamente ese propósito.

---

## ¿Qué hacen los guardrails?

Los guardrails ayudan a que un sistema:
- opere dentro de límites definidos
- reduzca riesgos
- evite comportamientos peligrosos
- mantenga reglas operativas
- proteja información sensible

No hacen que un sistema sea perfectamente seguro.

Pero sí ayudan a controlar daños y reducir errores.  Puedes leer más en la [documentación oficial de IBM](https://www.ibm.com/think/topics/ai-guardrails?utm_source=chatgpt.com).

---

## Ejemplos de guardrails

### 🔒 Validación de rutas

```python
os.path.commonpath(...)
```

Evita que el agente escape del `working_directory`.

---

### 🧠 System prompts

```text
Nunca reveles información sensible.
```

Definen reglas de comportamiento para el modelo.

---

### 🛠️ Restricción de tools

Un agente puede:
- leer archivos
- pero no borrarlos

Eso también es un guardrail.

---

### ⏱️ Timeouts

```python
timeout=30
```

Evita procesos infinitos o bloqueados.

---

### 📏 Límites de tamaño

```python
MAX_CHARS = 10000
```

Evita consumir demasiada memoria o tokens.

---

## Tipos de guardrails

Los guardrails pueden existir en distintas capas:

| Capa | Ejemplo |
|---|---|
| Prompt | reglas del system prompt |
| Tooling | filesystem restringido |
| Runtime | timeouts |
| Validación | schemas / JSON |
| Infraestructura | sandboxes / containers |
| Moderación | filtros de contenido |

---

## Guardrails y agentes

Los agentes modernos suelen:
- ejecutar herramientas
- leer archivos
- llamar APIs
- tomar decisiones autónomas

Eso introduce riesgos nuevos.

Por ejemplo:
- leer archivos sensibles
- ejecutar código peligroso
- seguir instrucciones maliciosas
- caer en prompt injection

Por eso los agentes reales utilizan múltiples capas de guardrails.  

Acá dejamos la [la documentación oficial de Guardrails de Langchain.](https://docs.langchain.com/oss/python/langchain/guardrails?utm_source=chatgpt.com) por si te interesa profundizar.

---

## Guardrails ≠ seguridad absoluta

Un guardrail no garantiza protección perfecta.

Los modelos todavía pueden:
- equivocarse
- ignorar instrucciones
- ser manipulados
- sufrir jailbreaks

Los guardrails reducen riesgos, pero no eliminan todos los problemas.En este [artículo de The Guardian](https://www.theguardian.com/technology/article/2024/may/20/ai-chatbots-safeguards-can-be-easily-bypassed-say-uk-researchers?utm_source=chatgpt.com) se muestra cómo se pueden eludir fácilmente medidas de seguridad en los LLMs.

---

## Guardrails en AI Agent Quest

El laboratorio ya utiliza varios guardrails:

- `working_directory`
- `MAX_CHARS`
- `temperature=0`
- validación de rutas
- `try/except`
- timeouts

Todos ayudan a mantener el comportamiento del agente dentro de límites controlados.

---

## Idea importante

Un agente poderoso sin límites claros no es útil.

Es peligroso.