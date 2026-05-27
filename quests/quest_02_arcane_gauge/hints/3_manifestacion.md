## La manifestación

```python
usage = response.usage_metadata
if usage is None:
    raise RuntimeError("No se recibió metadata de uso desde Gemini.")

print(f"Prompt tokens: {usage.prompt_token_count}")
print(f"Response tokens: {usage.candidates_token_count}")
```

El check valida que los strings exactos `Prompt tokens:` y `Response tokens:` aparezcan en stdout **antes** del texto del agente.
