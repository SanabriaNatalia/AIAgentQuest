# argparse

> *“Una herramienta útil no solo ejecuta órdenes.  
> También sabe escucharlas.”*  
> — Zhyréon

`argparse` es un módulo estándar de Python que permite crear programas de terminal capaces de recibir argumentos.

En AI Agent Quest lo usamos para que el agente reciba instrucciones desde consola sin tener que modificar el código, así como para parsarle opciones de ejecución ([flags](../terminal/flags.md)).

---

## ¿Por qué usar `argparse`?

Sin `argparse`, el prompt estaría fijo en el código:

```python
prompt = "Explícame qué es un agente IA"
```

Con `argparse`, el usuario puede enviarlo desde terminal:

```bash
uv run python -m quests.quest_03_user_input.starter.main "Explícame qué es un agente IA"
```

---

## Estructura básica

```python
import argparse

parser = argparse.ArgumentParser(
    description="AI Agent Quest"
)

parser.add_argument(
    "user_prompt",
    type=str,
    help="Prompt del usuario"
)

args = parser.parse_args()

prompt = args.user_prompt
```

---

## ¿Qué está pasando?

### `ArgumentParser`

Crea el objeto que interpreta los argumentos recibidos desde terminal.

```python
parser = argparse.ArgumentParser(description="AI Agent Quest")
```

---

### `add_argument`

Define qué argumento esperamos recibir.

```python
parser.add_argument("user_prompt", type=str, help="Prompt del usuario")
```

En este caso:

- `user_prompt` es obligatorio
- `type=str` indica que será texto
- `help` describe el argumento cuando usamos `-h`

---

### `parse_args`

Lee los argumentos reales enviados al ejecutar el programa.

```python
args = parser.parse_args()
```

Luego puedes acceder al valor así:

```python
args.user_prompt
```

---

## Ver ayuda del comando

`argparse` genera ayuda automáticamente.

```bash
uv run python -m quests.quest_03_user_input.starter.main -h
```

También puedes usar:

```bash
uv run python -m quests.quest_03_user_input.starter.main --help
```

---

## Argumentos posicionales

Un argumento posicional es obligatorio y depende de su posición.

```bash
uv run python -m quests.quest_03_user_input.starter.main "Hola agente"
```

Aquí:

```text
"Hola agente"
```

se convierte en:

```python
args.user_prompt
```

---

## ¿Qué pasa si no envío el argumento?

Si ejecutas el programa sin prompt:

```bash
uv run python -m quests.quest_03_user_input.starter.main
```

`argparse` detiene el programa y muestra un mensaje de error indicando qué argumento falta.

Eso es útil porque evita que tengas que validar todo manualmente.

---

## Flags opcionales

Argparse también permite añadir [flags](../terminal/flags.md) (argumentos opcionales) en la ejecución del programa:

```python
parser.add_argument(
    "--verbose",
    action="store_true",
    help="Mostrar información adicional"
)
```

Y usarlo así:

```bash
uv run python -m quests.quest_03_user_input.starter.main "Hola agente" --verbose
```

Si el usuario incluye `--verbose`, entonces:

```python
args.verbose
```

será `True`.

Si no lo incluye, será `False`.

---

## Idea clave

`argparse` convierte un script de Python en una herramienta de terminal más flexible.