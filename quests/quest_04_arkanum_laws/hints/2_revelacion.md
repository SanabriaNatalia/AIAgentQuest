## La revelación

La llamada `client.models.generate_content(...)` acepta un parámetro `config=` que recibe un **`types.GenerateContentConfig`**. Dentro de esa configuración van:

- `system_instruction=` — el `system_prompt` que define las reglas del agente.
- `temperature=` — el grado de determinismo de la respuesta. Q04 pide `0` para que las respuestas no varíen entre corridas.

Antes de conectar nada, edita **`common/prompts/system_prompt.py`** con el texto exacto que pide el quest (la frase clave `"LAS LEYES DEL ARKANUM SON ABSOLUTAS."` debe estar dentro). Luego impórtala con `from common.prompts.system_prompt import system_prompt`.
