from common.progress.db import get_connection, init_db
from common.utils.ui import show_quest_header, success, warning

STARTING_RANK = "Aprendiz del Arkanum"

def main() -> None:
    show_quest_header(
        "Registro del Aprendiz",
        "Bienvenido al laboratorio, aprendiz. ¿Cómo debería llamarte?",
    )

    init_db()

    username = input("Ingresa tu nombre: ").strip()

    if not username:
        warning("El nombre no puede estar vacío.")
        return

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT username FROM apprentice WHERE id = 1"
        ).fetchone()

        if existing:
            warning(f"Ya existe un aprendiz registrado: {existing[0]}")
            return

        conn.execute(
            """
            INSERT INTO apprentice (id, username, current_rank)
            VALUES (1, ?, ?)
            """,
            (username, STARTING_RANK),
        )

    success(f"Aprendiz registrado: {username}")
    success(f"Rango inicial: {STARTING_RANK}")


if __name__ == "__main__":
    main()