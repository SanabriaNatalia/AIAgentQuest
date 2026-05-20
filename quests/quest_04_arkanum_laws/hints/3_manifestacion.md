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

`system_instruction` y `contents` son canales distintos: uno define **quién eres**, el otro **qué te están preguntando**. Por eso las leyes del Arkanum dominan sobre cualquier pregunta del usuario.
