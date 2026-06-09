## El susurro

> El modelo te pide "ejecuta `get_files_info` con `directory='.'`". Tienes el diccionario de funciones reales. ¿Cómo conectas el nombre que llega con la función que corresponde, y le devuelves el resultado en el formato que el modelo entiende como observación?

Son dos pasos separados: (1) **ejecutar** la función real desde el `function_map`, y (2) **envolver** su retorno en un `types.Content` con `role="tool"`.
