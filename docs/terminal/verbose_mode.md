# Verbose Mode

> *“Un aprendiz observa los resultados.  
> Un artífice observa el proceso.”*  
> — Zhyréon

Muchos programas de terminal ofrecen un modo especial llamado:

```text
verbose
```

Verbose significa:

> mostrar información adicional sobre lo que está ocurriendo internamente.

---

## ¿Por qué existe?

Normalmente, un programa intenta mostrar solo la información importante.

Ejemplo:

```text
Archivo creado correctamente.
```

Pero durante desarrollo o debugging, muchas veces queremos ver más detalles:
- qué está ejecutando el programa
- qué funciones está llamando
- cuántos tokens consumió
- qué respuestas recibió
- qué herramientas está usando

Ahí es donde entra el verbose mode.

---

## Cómo se activa

En terminal, normalmente usamos un [flag](flags.md):

```bash
--verbose
```

Ejemplo:

```bash
uv run python main.py "hola" --verbose
```

---

### ¿Qué es un flag?

Un flag es un argumento opcional que modifica el comportamiento del programa.

Normalmente los flags comienzan con:

```text
--
```

Ejemplos comunes:

```bash
--help
--version
--verbose
--debug
```

---

## Verbose en argparse

Con `argparse`, normalmente se configura así:

```python
parser.add_argument(
    "--verbose",
    action="store_true",
    help="Muestra información detallada",
)
```

### ¿Qué hace store_true?

Esto significa:

```text
si el usuario escribe --verbose:
    args.verbose = True

si no lo escribe:
    args.verbose = False
```

---

## Ejemplo práctico

Programa:

```python
if args.verbose:
    print("Mostrando información detallada...")
```

Terminal:

```bash
uv run python main.py "hola" --verbose
```

Resultado:

```text
Mostrando información detallada...
```

---

## Verbose mode en agentes IA

En sistemas de agentes, verbose mode es extremadamente útil.

Permite observar:
- prompts enviados
- tool calls
- tokens consumidos
- respuestas de herramientas
- reasoning intermedio
- errores
- loops del agente

Sin verbose mode, muchas veces el agente parece una caja negra.

---

## Ejemplo en AI Agent Quest

```text
Calling function: get_files_info({'directory': '.'})
-> {'result': 'Result for current directory: ...'}
```

Esto nos permite observar:
- qué decidió hacer el modelo
- qué ejecutó realmente el programa
- qué resultado devolvió la tool

---

## Idea importante

Verbose mode no cambia la lógica del programa.

Solo cambia:
> cuánto puedes observar del proceso interno.