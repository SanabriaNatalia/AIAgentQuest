## La revelación

Dos APIs nuevas:

- **`argparse.ArgumentParser`** + `parser.add_argument("user_prompt")` — para capturar el mensaje desde la línea de comandos.
- **`types.Content`** y **`types.Part`** — clases del SDK que envuelven el texto del usuario junto con un `role`. El modelo conversacional ya no espera strings sueltos; espera mensajes etiquetados con su rol.

Una vez tengas la lista `messages` de `Content`, pásala a `generate_content` con `contents=messages` (en plural, ya no `contents=prompt`).
