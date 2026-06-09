## La manifestación

Dentro de `common/functions/get_valid_target_path.py`:

```python
working_dir_abs = os.path.abspath(working_directory)
raw_target_path = os.path.join(working_dir_abs, target_path)
resolved_target_path = os.path.abspath(raw_target_path)
is_valid_path = os.path.commonpath([working_dir_abs, resolved_target_path]) == working_dir_abs
```

Si `is_valid_path` es `False`, el `RuntimeError` que ya está escrito en el archivo se dispara. Termina retornando `resolved_target_path`. En el starter del quest, los bucles ya están — solo tienes que llamar a `get_valid_target_path(WORKING_DIRECTORY, path)` dentro de un `try/except`.
