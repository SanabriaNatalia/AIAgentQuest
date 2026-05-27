## La manifestación

```python
parser = argparse.ArgumentParser()
parser.add_argument("user_prompt")
args = parser.parse_args()
prompt = args.user_prompt

messages = [
    types.Content(role="user", parts=[types.Part(text=prompt)])
]
```

La lista `messages` arranca con un único elemento. En los quests siguientes irás agregando más mensajes (respuestas del modelo, observaciones de tools) para construir un historial conversacional.
