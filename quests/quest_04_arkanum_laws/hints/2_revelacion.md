## La revelación

La llamada `client.models.generate_content(...)` acepta un parámetro `config=` que recibe un **`types.GenerateContentConfig`**. Dentro de esa configuración viven:

- `system_instruction=` — donde inyectas tu `system_prompt`.
- `temperature=` — donde fijas la consistencia. Q04 te pide `0` para que las respuestas no varíen entre corridas.

Antes de cablear nada, edita **`common/prompts/system_prompt.py`** con el texto exacto que pide el quest (la frase clave `"LAS LEYES DEL ARKANUM SON ABSOLUTAS."` debe estar dentro). Luego impórtala con `from common.prompts.system_prompt import system_prompt`.
