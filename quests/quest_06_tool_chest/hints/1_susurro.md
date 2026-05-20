## El susurro

> El modelo ya sabe pedirte cosas; lo que falta es enseñarle qué puede pedir. Abre `common/functions/get_files_info.py` y observa cómo se declara `schema_get_files_info`. ¿Qué tienen las otras tres funciones del repo que aún no tienen ese mismo patrón?

Una función sin schema es invisible para el agente. Y un schema sin registrar en la `Tool` también lo es.
