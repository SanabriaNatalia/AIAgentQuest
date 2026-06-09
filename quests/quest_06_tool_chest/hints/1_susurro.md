## El susurro

> El modelo ya sabe responder, pero no sabe qué funciones tienes disponibles. Abre `common/functions/get_files_info.py` y observa cómo se declara `schema_get_files_info`. ¿Qué les falta a las otras tres funciones del repo para tener ese mismo patrón?

Una función sin schema no es visible para el modelo (no la puede pedir). Y un schema sin registrar en la `Tool` que se pasa al config tampoco lo es.
