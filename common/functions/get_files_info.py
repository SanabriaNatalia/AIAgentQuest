from common.functions.get_valid_target_path import get_valid_target_path
import os


def get_files_info(working_directory, directory="."):
    
    answer : str = ""

    if directory == ".":
        answer = "Result for current directory:\n"
    else:
        answer = f"Result for '{directory}' directory:\n"
    
    try:
        target_dir = get_valid_target_path(
            working_directory,
            directory,
        )

        if not os.path.isdir(target_dir):
            raise RuntimeError(f"'{directory}' is not a directory")
        
        items = os.listdir(target_dir)
                
        for item in items:
            item_path = os.path.join(target_dir, item)
            answer = answer + f"- {item}: file_size={os.path.getsize(item_path)}, is_dir={os.path.isdir(item_path)}\n"

        return answer

    except Exception as e:
        error_str = f"Error: {e}"
        return answer + error_str
