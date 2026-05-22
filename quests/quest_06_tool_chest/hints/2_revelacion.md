## La revelación

Cada herramienta necesita un **`types.FunctionDeclaration`** con tres campos:

- `name` — el identificador exacto que el modelo invocará.
- `description` — una frase corta que el modelo lee para decidir cuándo usar la herramienta.
- `parameters` — un **`types.Schema`** que describe qué argumentos espera (`type`, `properties`, `required`).

Una vez declarados los 4 schemas (`get_files_info`, `get_file_content`, `write_file`, `run_python_file`), regístralos en `common/functions/call_function.py` dentro de `available_functions = types.Tool(function_declarations=[...])`. En el starter, pasa la tool al config con `tools=[available_functions]` y revisa `response.function_calls` tras la respuesta.
