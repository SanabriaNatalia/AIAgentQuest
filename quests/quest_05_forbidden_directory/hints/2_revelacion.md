## La revelación

Tres funciones del módulo `os.path` resuelven el quest:

- **`os.path.abspath(path)`** — convierte cualquier ruta a su forma absoluta y normalizada.
- **`os.path.join(base, target)`** — une dos fragmentos respetando los separadores del sistema operativo.
- **`os.path.commonpath([a, b])`** — devuelve el prefijo común entre dos rutas absolutas. Si `b` está dentro de `a`, el `commonpath` será exactamente `a`.

La validación se reduce a comparar `commonpath([working_dir_abs, resolved_target_path])` con `working_dir_abs`. Si difieren, la ruta está fuera del directorio permitido.
