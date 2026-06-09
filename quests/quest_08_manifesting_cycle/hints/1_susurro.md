## El susurro

> Una sola acción no basta: el agente lee, escribe, ejecuta, y luego necesita ver el resultado para decidir el siguiente paso. ¿Cómo construyes ese ciclo de acción → observación → nueva acción, sin caer en un loop infinito?

La lista `messages` es la memoria compartida entre iteraciones: cada respuesta del modelo y cada resultado de tool se agrega al historial, y la siguiente iteración los usa como contexto.
