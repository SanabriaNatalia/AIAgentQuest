## La manifestación

Cuerpo de `call_function` dentro de `common/functions/call_function.py`:

```python
function_name = function_call.name or ""
if function_name not in function_map:
    return types.Content(
        role="tool",
        parts=[types.Part.from_function_response(
            name=function_name,
            response={"error": f"Unknown function: {function_name}"},
        )],
    )

args = dict(function_call.args) if function_call.args else {}
args["working_directory"] = "quests/quest_07_agent_incarnation/workspace"
function_result = function_map[function_name](**args)

return types.Content(
    role="tool",
    parts=[types.Part.from_function_response(name=function_name, response={"result": function_result})],
)
```

El `role="tool"` es lo que separa una **observación** (resultado de tool) de un **mensaje del usuario** o de un **mensaje del agente** en el historial. Sin él, el modelo no sabe distinguir.
