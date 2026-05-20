## La revelación

Tres piezas resuelven el cuerpo de `call_function`:

- **`function_map[name](**args)`** — despacha al callable real usando el nombre que viene del `function_call`.
- **`args["working_directory"] = "quests/quest_07_agent_incarnation/workspace"`** — inyectado por ti, **nunca** por el modelo. El agente no controla su propio jardín.
- **`types.Content(role="tool", parts=[types.Part.from_function_response(name=..., response={"result": ...})])`** — el formato exacto que Gemini espera como observación de una tool.

Si `function_name` no existe en `function_map`, devuelve un `Content` con `response={"error": f"Unknown function: {function_name}"}`. Nunca dejes propagar una `KeyError`.

En el starter del quest agrega también el flag `--verbose` con `parser.add_argument("--verbose", action="store_true", ...)` y reemplaza el `print` de Q06 por llamadas a `call_function(...)` que acumules en `function_results`.
