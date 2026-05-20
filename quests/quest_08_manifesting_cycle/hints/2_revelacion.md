## La revelación

El loop tiene tres elementos clave:

- **`for _ in range(MAX_ITERS)`** — la frontera contra ciclos infinitos. `MAX_ITERS` se importa de `common.config`.
- Después de cada respuesta del modelo: **`messages.append(candidate.content)`** para que la siguiente iteración recuerde qué se pidió.
- Después de ejecutar tools: **`messages.append(types.Content(role="tool", parts=function_results))`** para entregar la observación al modelo.

La salida es simple: si `response.function_calls` viene vacío, el modelo dio una respuesta final → `return response.text` desde `generate_content` y el loop en `main()` rompe imprimiéndola. Si las iteraciones se agotan sin respuesta final, imprime `Maximum iterations ({MAX_ITERS}) reached.`
