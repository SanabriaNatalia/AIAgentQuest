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

En los quests con agent loop (Q07 y Q08), `arkanum run` decide **cuánto** ves según pongas o no `--verbose`. El agente hace exactamente lo mismo en ambos casos; solo cambia el detalle que se imprime en tu terminal.

**Sin `--verbose`** — vista limpia, solo el esqueleto del ciclo:

```text
· Iteración 1/20
  🛠 get_files_info(directory=".")
     ↳ ok (155 B)
· Iteración 2/20
  🛠 get_file_content(file_path="calculator.py")
     ↳ ok (204 B)
🤖 Agente:
Las operaciones disponibles son: add, subtract, multiply, divide.
```

**Con `--verbose`** — además los tokens por iteración, los argumentos completos y el resultado completo de cada tool:

```text
· Iteración 1/20
  · tokens · prompt 1234 · respuesta 56
  🛠 get_files_info(directory=".")
     ↳ ok
       - calculator.py: 812 bytes, is_dir=False
       - tests.py: 1.1 KB, is_dir=False
```

Esto nos permite observar:
- qué decidió hacer el modelo
- qué ejecutó realmente el programa
- qué resultado devolvió la tool

> ℹ️ El dashboard `/live-agent` guarda **siempre** el detalle completo, lo pongas o no en la terminal. Allí el toggle **🔍 Verbose** filtra lo mismo sobre la timeline: apagado muestra el esqueleto; encendido añade tokens, latencia, memoria del loop y el razonamiento del agente.

---

## Idea importante

Verbose mode no cambia la lógica del programa.

Solo cambia:
> cuánto puedes observar del proceso interno.