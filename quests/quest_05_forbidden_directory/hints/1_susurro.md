## El susurro

> Tienes dos rutas absolutas: el `working_directory` permitido y la ruta de destino. ¿Cómo verificas, sin ambigüedad, que la segunda está dentro de la primera?

Comparar los strings directamente no funciona: `../foo` y `foo/../foo` se ven distintos pero pueden apuntar al mismo lugar. Necesitas comparar las rutas ya normalizadas, no su forma textual.
