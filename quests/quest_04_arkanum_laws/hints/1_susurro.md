## El susurro

> Para que el modelo siga reglas fijas en todas las llamadas, no las agregues al prompt del usuario: usa el canal aparte que ofrece la API. ¿En qué parámetro de `generate_content` se configura?

No es `contents`. Es el parámetro que recibe la configuración de la llamada — ahí adentro vive el `system_instruction`.
