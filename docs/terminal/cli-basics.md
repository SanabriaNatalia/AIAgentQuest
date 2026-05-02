# CLI Basics

> *“Antes de invocar agentes, aprende a moverte por el templo.”*  
> — Zhyréon

La **CLI** (*Command Line Interface*) es una forma de interactuar con tu computador usando texto.

En lugar de hacer clic en carpetas o botones, escribes comandos.

En Arkanum usarás la terminal para:

- ejecutar Quests
- correr validaciones
- pasar prompts al agente
- leer errores
- explorar comandos

---

## Comandos básicos

### Ver dónde estás

```bash
pwd
```

Muestra la carpeta actual.

---

### Listar archivos

```bash
ls
```

En Windows PowerShell también puedes usar:

```powershell
dir
```

---

### Entrar a una carpeta

```bash
cd nombre_de_carpeta
```

Ejemplo:

```bash
cd ai-agent-quest
```

---

### Volver una carpeta atrás

```bash
cd ..
```

---

### Limpiar la terminal

```bash
clear
```

En Windows:

```powershell
cls
```

---

## Ejecutar código Python con uv

En este proyecto usamos `uv`.

Para ejecutar un Quest usamos:

```bash
uv run python -m quests.quest_01_first_agent.starter.main
```

La parte importante es:

```bash
python -m
```

Eso ejecuta el archivo como módulo de Python y ayuda a que los imports funcionen correctamente.

---

## Pasar texto como argumento

Algunos Quests reciben un prompt desde consola:

```bash
uv run python -m quests.quest_03_user_input.starter.main "¿Qué es un agente IA?"
```

El texto entre comillas se envía al programa como argumento.

También existen otro tipo de parámetros u opciones llamados flags. Puedes leer más al respecto [aquí](./flags.md).

---

## Leer errores

Cuando algo falla, la terminal suele mostrar un traceback.

Aunque parezca intimidante, busca estas dos cosas:

```text
ModuleNotFoundError
```

indica un problema de imports.

```text
RuntimeError
```

normalmente indica que el programa detectó un problema esperado, como una API key faltante.

---

## Regla de oro

Ejecuta los comandos desde la raíz del proyecto.

Es decir, desde la carpeta donde están:

```text
README.md
pyproject.toml
quests/
common/
docs/
```

Si estás en otra carpeta, los imports pueden fallar.