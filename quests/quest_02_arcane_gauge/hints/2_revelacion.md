## La revelación

La metadata de uso vive en **`response.usage_metadata`**. Es un objeto con varios contadores; los dos que importan ahora son:

- `prompt_token_count` — tokens consumidos por tu mensaje (entrada).
- `candidates_token_count` — tokens consumidos por la respuesta del modelo (salida).

Si `usage_metadata` viene `None`, algo salió mal en la llamada: lanza un `RuntimeError`. Imprime los tokens **antes** de mostrar la respuesta del agente — el check valida ese orden.
