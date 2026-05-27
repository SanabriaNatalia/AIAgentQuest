## La manifestación

```python
client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)
```

Las dos llamadas viven separadas: primero creas el cliente, luego usas su método `generate_content` para enviar el prompt. Recuerda también definir un `prompt` no vacío (el quest pide pedirle al modelo que explique qué es un agente IA).
