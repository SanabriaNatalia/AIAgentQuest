## El susurro

> El modelo dice "ejecuta `get_files_info` con `directory='.'`". Tú tienes el diccionario de funciones reales. ¿Cómo despachas el nombre que te llega a la función que toca, y le devuelves un resultado que el modelo entienda como observación?

Dos pasos separados: **ejecutar** la función real y **envolver** su retorno en una `Content` con el rol correcto.
