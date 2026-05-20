## La revelación

El laboratorio expone dos conjuros clave del módulo `google.genai`:

- **`genai.Client`** — constructor del cliente. Acepta un argumento nombrado `api_key`.
- **`client.models.generate_content`** — método del cliente que envía el prompt y devuelve la respuesta.

Guarda el cliente en una variable (`client = ...`) y luego guarda el resultado de `generate_content` en otra (`response = ...`). El texto del modelo vive en `response.text`.
