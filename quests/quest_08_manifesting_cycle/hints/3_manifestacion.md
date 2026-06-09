## La manifestación

Esqueleto del ciclo. La lógica concreta de tools dentro de `generate_content` la tomas de tu Q07:

```python
def main():
    # ... validar api_key, parser, args, messages iniciales ...
    for _ in range(MAX_ITERS):
        final_text = generate_content(messages, args.verbose)
        if final_text is not None:
            print(final_text)
            return
    print(f"Maximum iterations ({MAX_ITERS}) reached.")

def generate_content(messages, verbose=False):
    response = client.models.generate_content(...)
    if response.candidates:
        for candidate in response.candidates:
            if candidate.content:
                messages.append(candidate.content)
    if not response.function_calls:
        return response.text
    # ... ejecutar tools, llenar function_results ...
    messages.append(types.Content(role="tool", parts=function_results))
    return None
```

`return None` significa "sigue iterando"; `return response.text` rompe el bucle desde `main()`.
