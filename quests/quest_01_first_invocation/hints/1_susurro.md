## El susurro

> Importaste `genai`, pero ¿en qué momento creas una instancia concreta del cliente con tu API key? Y una vez creada, ¿quién es el responsable de enviarle el prompt y devolverte la respuesta?

Importar un módulo no es lo mismo que instanciar un cliente. Y un cliente instanciado no hace nada hasta que llamas a uno de sus métodos.
