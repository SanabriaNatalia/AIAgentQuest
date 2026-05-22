# workspace/

Territorio permitido del agente.

A partir del **Acto II** (Quest 05+) los agentes leen, escriben, modifican y
ejecutan archivos dentro de un `workspace/`. Esta carpeta es ese sandbox:
todo lo que el agente toque debería vivir aquí.

Sin estos límites, un agente podría acceder a archivos sensibles o modificar
contenido del proyecto por accidente. La validación que aprenderás a
construir en Quest 05 (`get_valid_target_path`) garantiza que ninguna ruta
escape de esta carpeta.

> Cada quest del Acto II también incluye su propio `workspace/` interno con
> los archivos de prueba específicos del ejercicio. Esta carpeta raíz queda
> como sandbox libre para tus propios experimentos.
