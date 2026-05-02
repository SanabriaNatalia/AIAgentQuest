import os

def get_valid_target_path(working_directory, target_path):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_path_abs = os.path.normpath(os.path.join(working_dir_abs, target_path))
        valid_target_path = os.path.commonpath([working_dir_abs, target_path_abs]) == working_dir_abs
    
        if not valid_target_path:
            raise RuntimeError(f"Cannot access '{target_path}' as it is outside the permitted working directory")

        return target_path_abs

    except Exception as e:
        error_str = f"Error: {e}"
        return error_str