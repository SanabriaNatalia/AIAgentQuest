from common.config import MAX_CHARS
from common.functions.get_valid_target_path import get_valid_target_path
from google.genai import types
import os

# TODO 3 - Quest 6: Define el schema para la función get_file_content, 
# similar a schema_get_files_info
schema_get_file_content = None

def get_file_content(working_directory, file_path):
    try:
        target_file = get_valid_target_path(
            working_directory,
            file_path,
        )   

        if not os.path.isfile(target_file):
            raise RuntimeError(f"File not found or is not a regular file: '{target_file}'")
        
        with open(target_file, mode='r') as file:
            file_content_string = file.read(MAX_CHARS)
            if file.read(1):
                file_content_string = file_content_string + f"[...File '{file_path}' truncated at {MAX_CHARS} characters]"
        
        return file_content_string

    except Exception as e:
        error_str = f"Error: {e}"
        return error_str
