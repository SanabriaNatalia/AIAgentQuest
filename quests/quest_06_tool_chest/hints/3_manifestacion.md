## La manifestación

Plantilla para uno de los schemas faltantes (la repites para los otros dos):

```python
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the text content of a file inside the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(type=types.Type.STRING, description="Path relative to working directory"),
        },
        required=["file_path"],
    ),
)
```

`working_directory` **no** se declara — lo inyectarás tú en el Quest 07. El modelo sólo conoce los args que el agente le permite controlar.
