from common.progress.db import get_connection, init_db
from common.utils.ui import show_quest_header, success, warning


def main() -> None:
    show_quest_header(
        "Progreso del Aprendiz",
        "Los ecos del viaje quedan registrados.",
    )

    init_db()

    with get_connection() as conn:
        apprentice = conn.execute(
            "SELECT username, current_rank FROM apprentice WHERE id = 1"
        ).fetchone()

        if apprentice is None:
            warning("No hay aprendiz registrado.")
            warning("Ejecuta: uv run python -m common.progress.init_user")
            return

        completed = conn.execute(
            """
            SELECT quest_id, completed_at
            FROM quest_completion
            ORDER BY completed_at
            """
        ).fetchall()

    username, current_rank = apprentice

    success(f"Aprendiz: {username}")
    success(f"Rango actual: {current_rank}")

    if not completed:
        warning("Aún no hay Quests completados.")
        return

    print("\nQuests completados:")
    for quest_id, completed_at in completed:
        print(f"- {quest_id} · {completed_at}")


if __name__ == "__main__":
    main()