## La revelación

La medida del costo vive en **`response.usage_metadata`**. Es un objeto con varios contadores; los dos que importan ahora son:

- `prompt_token_count` — lo que costó **tu** mensaje.
- `candidates_token_count` — lo que costó la **respuesta** del modelo.

Si `usage_metadata` viene `None`, algo salió mal en la invocación: protégete con un `RuntimeError`. Recuerda imprimir los tokens **antes** de mostrar la respuesta — el orden importa para el check.
