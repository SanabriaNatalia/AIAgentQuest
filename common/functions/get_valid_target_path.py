import os


def get_valid_target_path(
    working_directory: str,
    target_path: str
) -> str:
    """
    Construye una ruta segura dentro del working_directory.

    Si target_path intenta escapar del working_directory,
    lanza RuntimeError.
    """
    working_dir_abs = os.path.abspath(working_directory)

    raw_target_path = os.path.join(working_dir_abs, target_path)

    resolved_target_path = os.path.normpath(raw_target_path)

    is_valid_path = (
        os.path.commonpath([working_dir_abs, resolved_target_path])
        == working_dir_abs
    )

    if not is_valid_path:
        raise RuntimeError(
            f"'{target_path}' is outside the permitted working directory"
        )

    return resolved_target_path
