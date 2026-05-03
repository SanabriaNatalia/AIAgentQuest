import os


def get_valid_target_path(
    working_directory: str,
    target_path: str
) -> str:
    """
    Construye una ruta segura dentro del working_directory.

    Si target_path intenta escapar del working_directory,
    debe lanzar RuntimeError.
    """

    # TODO 1:
    # Convierte working_directory en una ruta absoluta.
    working_dir_abs = ""

    # TODO 2:
    # Construye la ruta objetivo uniendo working_dir_abs y target_path.
    raw_target_path = ""

    # TODO 3:
    # Normaliza la ruta objetivo.
    resolved_target_path = ""

    # TODO 4:
    # Verifica que resolved_target_path siga dentro de working_dir_abs.
    is_valid_path = ...

    # TODO 5:
    # Si la ruta no es válida, lanza RuntimeError.
    if not is_valid_path:
        raise RuntimeError(
            f"'{target_path}' is outside the permitted working directory"
        )

    # TODO 6:
    # Retorna la ruta validada.
    return ...