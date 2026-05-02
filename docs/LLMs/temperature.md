# Temperatura

> *“No todas las respuestas nacen con el mismo nivel de caos.”*  
> — Zhyréon

Los modelos de lenguaje no siempre generan exactamente la misma respuesta.

La **temperatura** controla el nivel de variabilidad durante la generación de texto.

---

## ¿Qué hace la temperatura?

La temperatura influye en qué tan:
- predecibles
- creativas
- variadas

serán las respuestas del modelo.

---

### Temperaturas bajas

Ejemplo:

```python
temperature=0
```

Generan respuestas más:
- consistentes
- determinísticas
- repetibles
- conservadoras

Esto es útil para:
- testing
- validaciones
- agentes
- workflows estructurados
- generación de código
- formatos estrictos

---

### Temperaturas altas

Ejemplo:

```python
temperature=1.5
```

Generan respuestas más:
- creativas
- impredecibles
- variadas

Esto puede ser útil para:
- brainstorming
- escritura creativa
- generación de ideas
- narrativa

---

### Ejemplo conceptual

Prompt:

```text
Describe un dragón.
```

#### Temperatura baja

```text
Un dragón es una criatura reptiliana de gran tamaño...
```

#### Temperatura alta

```text
Las montañas temblaron cuando el dragón de obsidiana
desplegó alas cubiertas de ceniza brillante...
```

---

## Determinismo

Con temperaturas bajas, el modelo tiende a producir respuestas similares entre ejecuciones.

Eso es importante cuando:
- necesitas resultados consistentes
- quieres validar salidas automáticamente
- estás construyendo agentes

---

## ¿Temperatura = inteligencia?

No.

Una temperature alta no hace que el modelo sea “más inteligente”.

Solo aumenta la variabilidad durante la generación.

---

## Uso en Gemini

Ejemplo:

```python
config=types.GenerateContentConfig(
    temperature=0
)
```

---

## Rangos comunes

No todos los modelos utilizan exactamente el mismo rango de temperatura.

Algunos ejemplos comunes:

| Provider | Rango típico |
|---|---|
| OpenAI | `0 → 2` |
| Gemini | `0 → 2` |
| Anthropic | `0 → 1` |

Los valores exactos dependen del modelo y del proveedor.

---

## Valores habituales

| Temperatura | Comportamiento |
|---|---|
| `0` | 🔢 muy determinístico |
| `0.2` | ⚙️ estable |
| `0.5` | ⚖️ balanceado |
| `0.8` | ✨ creativo moderado |
| `1.0` | 🎭 bastante variado |
| `1.5+` | 🌀 empieza el caos |
| `2.0` | 👹 goblin mode |

En agentes modernos, especialmente aquellos que:
- usan tools
- generan código
- producen JSON
- ejecutan workflows

es común utilizar:

```python
temperature=0
```

para maximizar consistencia y estabilidad.

---

## Idea importante

La temperatura no controla cuánto “sabe” el modelo.

Controla cuánto se desvía de las respuestas más probables.