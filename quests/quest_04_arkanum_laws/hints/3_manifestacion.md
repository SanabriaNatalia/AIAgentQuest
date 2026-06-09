## La manifestación

```python
from common.prompts.system_prompt import system_prompt

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=messages,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0,
    ),
)
```

`system_instruction` y `contents` son parámetros distintos: el primero define las reglas del modelo (no varían entre llamadas), el segundo es la conversación con el usuario. Por eso las reglas del system prompt prevalecen sobre lo que escriba el usuario.
