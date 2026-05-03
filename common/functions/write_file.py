import os

from google.genai import types
from common.functions.get_valid_target_path import get_valid_target_path


# TODO 3 - Quest 6: Define el schema para la función write_file, 
# similar a schema_get_files_info
schema_get_file_content = None

def write_file(working_directory, file_path, content):
    try:
        target_file = get_valid_target_path(
            working_directory,
            file_path,
        )   
    
        if os.path.isdir(target_file):
            raise RuntimeError(f"Cannot write to '{file_path}' as it is a directory")
        
        parent_dir = os.path.dirname(target_file)
        os.makedirs(parent_dir, exist_ok=True)

        with open(target_file, mode='w') as file:
            file.write(content)
        
        return f"Successfully wrote to '{file_path}' ({len(content)} characters written)"

    except Exception as e:
        error_str = f"Error: {e}"
        return error_str