## La revelación

Tres piezas resuelven el cuerpo de `call_function`:

- **`function_map[name](**args)`** — despacha al callable real usando el nombre que viene del `function_call`.
- **`args["working_directory"] = "quests/quest_07_agent_incarnation/workspace"`** — inyectado por ti, **nunca** por el modelo. El `working_directory` no debe ser controlable por el agente (es parte del guardrail de seguridad).
- **`types.Content(role="tool", parts=[types.Part.from_function_response(name=..., response={"result": ...})])`** — el formato exacto que Gemini espera como observación de una tool.

Si `function_name` no existe en `function_map`, devuelve un `Content` con `response={"error": f"Unknown function: {function_name}"}`. No dejes que se propague un `KeyError`.

En el starter del quest agrega también el flag `--verbose` con `parser.add_argument("--verbose", action="store_true", ...)` y reemplaza el `print` del Q06 por llamadas a `call_function(...)` cuyos resultados acumules en `function_results`.
