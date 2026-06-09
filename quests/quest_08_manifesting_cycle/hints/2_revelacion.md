## La revelación

El loop tiene tres elementos clave:

- **`for _ in range(MAX_ITERS)`** — el límite duro para evitar loops infinitos. `MAX_ITERS` se importa de `common.config`.
- Después de cada respuesta del modelo: **`messages.append(candidate.content)`** para que la siguiente iteración tenga acceso a lo que ya dijo el modelo.
- Después de ejecutar tools: **`messages.append(types.Content(role="tool", parts=function_results))`** para entregarle al modelo el resultado de cada tool como observación.

La condición de salida es directa: si `response.function_calls` viene vacío, el modelo dio una respuesta final → `return response.text` desde `generate_content` y el loop en `main()` termina imprimiéndola. Si las iteraciones se agotan sin respuesta final, imprime `Maximum iterations ({MAX_ITERS}) reached.`
