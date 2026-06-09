# Módulos y `python -m`

> *“Un hechizo aislado falla.  
> Solo cobra fuerza dentro de su círculo.”*  
> — Zhyréon

En Python, cada archivo `.py` es un **módulo**, y una carpeta con un `__init__.py` es un **paquete**. El laboratorio está organizado en paquetes (`quests/`, `common/`), y eso cambia cómo se ejecutan los programas.

---

## ¿Por qué `python -m`?

Hay dos formas de ejecutar código Python:

```bash
python archivo.py
```

y:

```bash
python -m paquete.modulo
```

La primera ejecuta un archivo suelto. La segunda lo ejecuta **como parte de un paquete**, lo que hace que los imports absolutos (como `from common.utils.ui import ...`) funcionen correctamente.

---

## El problema de ejecutar el archivo directo

Los starters del laboratorio importan código compartido:

```python
from common.utils.ui import show_quest_header
```

Si ejecutas el archivo directo:

```bash
python quests/quest_01_first_invocation/starter/main.py
```

Python no sabe dónde está `common`, y verás:

```text
ModuleNotFoundError: No module named 'common'
```

Por eso usamos la forma con módulo:

```bash
uv run python -m quests.quest_01_first_invocation.starter.main
```

Fíjate: los `/` se vuelven `.` y se quita el `.py`.

---

## La regla de oro

Ejecuta siempre **desde la raíz del proyecto** (la carpeta donde están `quests/`, `common/`, `pyproject.toml`). Desde ahí, Python encuentra los paquetes.

---

## En el curso no escribes esto a mano

El CLI del laboratorio te ahorra la forma larga:

```bash
arkanum run 1
```

`arkanum run N` resuelve el módulo correcto y lo ejecuta por ti. Lo ves en [comandos del CLI](../cli/commands.md). La forma con `python -m` es la "vía manual" equivalente.

---

## Idea importante

Un módulo no vive solo: vive dentro de un paquete.

`python -m` ejecuta tu código respetando esa estructura, y por eso los imports funcionan.
