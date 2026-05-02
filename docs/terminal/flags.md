# Flags y Opciones

> *“Las herramientas hablan en símbolos.*
> *Los arquitectos aprenden a interpretarlos.”*
>
> — Zhyréon

Muchos programas de terminal aceptan opciones especiales llamadas *flags*.

Normalmente comienzan con:
- `-`
- `--`

Estas opciones modifican el comportamiento del programa.

---

## Mostrar ayuda

Uno de los flags más comunes es:

```bash
-h
```

o:

```bash
--help
```

Normalmente muestran ayuda sobre el comando.

Ejemplo:

```bash
uv run python -m quests.quest_03_user_input.starter.main -h
```

Salida aproximada:

```text
usage: main.py [-h] user_prompt

Chatbot

positional arguments:
  user_prompt  Prompt del usuario

options:
  -h, --help   show this help message and exit
```

---

## Argumentos vs Flags

### Argumento posicional

Es un valor obligatorio.

Ejemplo:

```bash
uv run main.py "Hola"
```

Aquí:

```text
"Hola"
```

es un argumento posicional.

---

### Flag

Es una opción adicional.

Ejemplo:

```bash
uv run main.py "Hola" --verbose
```

Aquí:

```text
--verbose
```

activa un modo más detallado.

---

## Flags comunes

| Flag | Significado común |
|---|---|
| `-h` | ayuda |
| `--help` | ayuda |
| `--verbose` | mostrar más información |
| `--version` | mostrar versión |
| `--debug` | modo debug |

---

## Convención importante

Muchos programas modernos siguen convenciones similares para sus flags.

Aprender a explorarlos es una habilidad muy útil cuando trabajas con:
- herramientas de desarrollo
- agentes
- CLIs
- automatización