# Variables de Entorno

> *“Los arquitectos prudentes no escriben secretos en piedra.”*  
> — Zhyréon

Muchos programas necesitan información sensible para funcionar:

- API keys
- contraseñas
- tokens
- credenciales

Guardar estos valores directamente en el código es una mala práctica.
Si una API key termina en un repositorio público, cualquier persona podría utilizarla.

Dependiendo del servicio, eso puede permitir:
- consumir recursos a tu nombre
- generar costos inesperados
- acceder a información privada
- utilizar tus sistemas sin autorización

En entornos empresariales, una credencial expuesta puede convertirse en un incidente de seguridad serio.

Incluso si borras el archivo después, Git conserva historial de cambios, por lo que la credencial podría seguir siendo recuperable.

Por eso las credenciales nunca deben:
- subirse a GitHub
- compartirse por chat
- aparecer en screenshots
- enviarse por correo sin protección

Para prevenir lo anterior utilizamos variables de entorno.

---

## ¿Qué es una variable de entorno?

Es un valor almacenado fuera del código que el programa puede leer mientras se ejecuta.

Por ejemplo:

```text
GEMINI_API_KEY
```

puede contener tu API key de Gemini.

---

## El archivo `.env`

Durante desarrollo, normalmente usamos un archivo llamado:

```text
.env
```
Este archivo contiene conjuntos de llave-valor que almacenan la información sensible.

Ejemplo:

```env
GEMINI_API_KEY="tu_api_key"
```

Usualmente, este archivo vive en la raíz del proyecto.

---

## ¿Por qué usar `.env`?

Porque:
- evita escribir secretos en el código
- facilita cambiar configuraciones
- permite compartir el proyecto sin compartir credenciales

---

## Nunca subas `.env` a GitHub

Los archivos `.env` suelen contener información sensible.

Por eso normalmente agregamos:

```text
.env
```

al archivo:

```text
.gitignore
```

---

## Cargar variables con `dotenv`

En este laboratorio usamos:

```python
python-dotenv
```

para cargar automáticamente las variables del archivo `.env`.

---

## Cargar el archivo

```python
from dotenv import load_dotenv

load_dotenv()
```

Esto carga las variables del archivo `.env` al entorno del programa.

---

## Leer variables

Luego podemos acceder a ellas usando:

```python
import os

api_key = os.environ.get("GEMINI_API_KEY")
```

---

## ¿Por qué usar `.get()`?

Porque evita errores si la variable no existe.

Si la variable no está definida:

```python
api_key = None
```

---

## Validar variables requeridas

Una práctica importante es validar que las variables existan antes de continuar.

Ejemplo:

```python
if api_key is None:
    raise RuntimeError(
        "No se encontró GEMINI_API_KEY"
    )
```

---

## Flujo completo

```python
import os

from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

if api_key is None:
    raise RuntimeError(
        "No se encontró GEMINI_API_KEY"
    )
```

---

## Variables comunes en agentes

| Variable | Uso |
|---|---|
| `GEMINI_API_KEY` | acceso a Gemini |
| `OPENAI_API_KEY` | acceso a OpenAI |
| `ANTHROPIC_API_KEY` | acceso a Claude |
| `DATABASE_URL` | conexión a base de datos |

---

## Regla importante

Si una API key aparece en:
- commits
- screenshots
- repositorios públicos

debe considerarse comprometida y reemplazarse.