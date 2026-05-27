## La revelación

El módulo `google.genai` expone dos piezas clave:

- **`genai.Client(api_key=...)`** — constructor del cliente. Recibe tu API key como argumento nombrado.
- **`client.models.generate_content(model=..., contents=...)`** — método del cliente que envía el prompt y devuelve la respuesta.

Guarda el cliente en una variable (`client = ...`) y el resultado de `generate_content` en otra (`response = ...`). El texto generado por el modelo está en `response.text`.
