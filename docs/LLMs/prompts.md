# Prompts

> *“No basta con hablarle al modelo.  
> Hay que saber qué pedirle.”*  
> — Zhyréon

Un **prompt** es el texto que le envías al modelo para pedirle algo. Es la materia prima de todo lo que hace un agente: la calidad de la respuesta depende, en gran parte, de la calidad del prompt.

---

## Anatomía de un buen prompt

Un prompt claro suele combinar:

- **Instrucción**: qué quieres que haga el modelo.
- **Contexto**: la información que necesita para hacerlo.
- **Formato de salida**: cómo quieres la respuesta.
- **Ejemplos** (opcional): muestras de la respuesta esperada.

Ejemplo:

```text
Resume el siguiente texto en 3 viñetas, en español.

Texto:
"..."
```

---

## Sé específico

Un prompt vago produce respuestas vagas.

```text
❌ Háblame de Python.
✅ Explica en 2 párrafos qué es Python y para qué se usa,
   para alguien que nunca ha programado.
```

Mientras más claros el objetivo, el formato y el público, mejor la respuesta.

---

## Da ejemplos (few-shot)

Mostrarle al modelo uno o dos ejemplos de lo que esperas suele mejorar mucho el resultado:

```text
Convierte estas frases a un tono formal.

Ejemplo:
"hola q tal" → "Buenos días, ¿cómo está?"

Ahora convierte:
"nos vemos manana"
```

---

## Pide un formato

Si necesitas la respuesta en una estructura concreta (lista, JSON, tabla), pídelo explícitamente:

```text
Devuelve SOLO un objeto JSON con las claves "titulo" y "resumen".
```

Esto es clave cuando tu programa va a **procesar** la respuesta.

---

## Itera

Casi nunca se acierta a la primera. Prueba un prompt, observa la respuesta, ajusta. La [temperatura](temperature.md) afecta cuánto varía esa respuesta entre intentos.

---

## Errores comunes

- **Ambigüedad**: no queda claro qué se pide.
- **Sobrecarga**: demasiadas instrucciones en un solo prompt.
- **Asumir contexto**: el modelo solo sabe lo que está en el prompt (y su entrenamiento).
- **No pedir formato**: y luego sorprenderse de que la salida no encaje en tu código.

---

## Prompt del usuario vs system prompt

El prompt que vimos aquí es el **prompt del usuario**: la petición concreta. Existe además el **system prompt**, una capa de instrucciones que define el comportamiento del agente en *todas* las interacciones. Lo vemos en [prompts de sistema](system_prompts.md).

---

## Idea importante

El modelo no adivina lo que quieres.

Un buen prompt es la diferencia entre una respuesta útil y una inútil.
