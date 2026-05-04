# Función `main`

> *“Un ritual poderoso necesita una entrada clara.”*  
> — Zhyréon

En Python, muchos programas usan esta estructura:

```python
def main():
    ...

if __name__ == "__main__":
    main()
```

Al principio puede parecer una fórmula mágica.

Pero en realidad resuelve un problema importante:
- separar definición y ejecución
- evitar comportamiento inesperado
- permitir reutilización del código

---

## Código top-level

Todo el código escrito directamente en un archivo se ejecuta inmediatamente.

Ejemplo:

```python
print("Hola aprendiz")
```

Si ejecutas:

```bash
python main.py
```

el mensaje aparece automáticamente.

---

## El problema

Supongamos este archivo:

```python
print("Inicializando sistema...")

def greet():
    print("Hola")
```

Ahora imaginemos que otro archivo hace:

```python
import main
```

¿Qué ocurre?

Python ejecutará TODO el código top-level del archivo importado.

Eso significa que aparecerá:

```text
Inicializando sistema...
```

aunque no queríamos ejecutar el programa completo.

---

## Separando ejecución y definición

La solución es mover la lógica principal dentro de una función:

```python
def main():
    print("Inicializando sistema...")
```

Ahora la función existe…
pero todavía no se ejecuta.

---

## `__name__`

Python tiene una variable especial llamada:

```python
__name__
```

Su valor depende de cómo se está utilizando el archivo.

### Cuando ejecutas directamente el archivo

Ejemplo:

```bash
python main.py
```

Python asigna:

```python
__name__ = "__main__"
```

### Cuando el archivo es importado

Ejemplo:

```python
import main
```

Python asigna:

```python
__name__ = "main"
```

### Entonces…

Esto:

```python
if __name__ == "__main__":
    main()
```

significa:

> “ejecuta main() SOLO si este archivo fue ejecutado directamente.”

---

## ¿Qué logramos con esto?

Ahora podemos:
- importar funciones sin ejecutar el programa completo
- separar lógica de ejecución
- organizar mejor el código
- facilitar testing
- construir programas más mantenibles

---

## Ejemplo completo

```python
def greet():
    print("Hola")

def main():
    print("Iniciando programa...")
    greet()

if __name__ == "__main__":
    main()
```

---

## Flujo real

Si ejecutas:

```bash
python main.py
```

ocurre:

```text
Iniciando programa...
Hola
```

Pero si haces:

```python
import main
```

no ocurre nada automáticamente.

Solo se importan:
- funciones
- clases
- variables

---

## ¿Por qué usamos main() en AI Agent Quest?

A medida que el laboratorio crece:
- aparecen loops
- múltiples funciones
- parsers
- tools
- orchestration

Mover la lógica principal a:

```python
main()
```

hace el sistema:
- más claro
- más modular
- más profesional

---

# Idea importante

`main()` organiza la ejecución.

`if __name__ == "__main__"` controla cuándo debe comenzar el programa.