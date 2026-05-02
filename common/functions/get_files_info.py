import os

def get_files_info(working_directory, directory="."):
    
    answer : str = ""

    if directory == ".":
        answer = "Result for current directory:\n"
    else:
        answer = f"Result for '{directory}' directory:\n"
    
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))
        valid_target_dir = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
    
        if not valid_target_dir:
            raise RuntimeError(f"Cannot list '{directory}' as it is outside the permitted working directory")

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
