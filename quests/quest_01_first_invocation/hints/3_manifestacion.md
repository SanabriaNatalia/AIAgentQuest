## La manifestación

```python
client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)
```

Las dos llamadas viven separadas: primero invocas al cliente, luego le pides una respuesta. Define también un `prompt` no vacío (el quest pide pedirle al modelo que explique qué es un agente IA).
