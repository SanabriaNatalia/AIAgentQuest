## La revelación

Dos invocaciones nuevas:

- **`argparse.ArgumentParser`** + `parser.add_argument("user_prompt")` — para capturar el mensaje desde la línea de comandos.
- **`types.Content`** y **`types.Part`** — estructuras que envuelven el texto del usuario con un `role`. El modelo conversacional ya no quiere strings sueltos; quiere mensajes etiquetados.

Una vez tengas la lista `messages` de `Content`, pásala a `generate_content` con `contents=messages` (en plural, no `contents=prompt`).
