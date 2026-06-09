## El susurro

> Necesitas dos cambios respecto al Quest 02: (1) leer el prompt desde la línea de comandos en lugar de hardcodearlo, y (2) enviarlo al modelo como un mensaje estructurado en vez de un string suelto.

Para (1) hay un módulo estándar de Python que probablemente ya conoces. Para (2), el SDK de Gemini expone tipos específicos que envuelven el texto junto con un `role`.
