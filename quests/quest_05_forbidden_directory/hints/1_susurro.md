## El susurro

> Dos rutas absolutas. La primera define el territorio del agente; la segunda es a donde quiere ir. ¿Cómo verificas, sin ambigüedad, que la segunda no escapó de la primera?

No basta comparar strings: `../foo` y `foo/../foo` se ven distintos pero apuntan al mismo sitio. Necesitas comparar rutas como **rutas**, no como texto.
