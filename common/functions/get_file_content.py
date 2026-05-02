from common.config import MAX_CHARS
import os

def get_file_content(working_directory, file_path):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))
        valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
    
        if not valid_target_file:
            raise RuntimeError(f"Cannot read '{file_path}' as it is outside the permitted working directory")

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
