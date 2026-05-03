import os
import subprocess

from google.genai import types
from common.functions.get_valid_target_path import get_valid_target_path


def run_python_file(working_directory, file_path, args=None):
    try:
        target_file = get_valid_target_path(
            working_directory,
            file_path,
        )
        
        if not os.path.isfile(target_file):
            raise RuntimeError(f'"{file_path}" does not exists or is not a regular file')
    
        if not file_path.endswith(".py"):
            raise RuntimeError(f'"{file_path}" is not a Python file')
        
        working_dir_abs = os.path.abspath(working_directory)
        command = ["python", target_file]

        if args:
            command.extend(args)

        result = subprocess.run(
            command,
            cwd=working_dir_abs,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        answer = ""

        if result.returncode != 0:
            answer = answer +f"Process exited with code {result.returncode}\n"
        
        if not output and not error:
            answer = answer + f"No output produced\n"
        
        return answer +f"STDOUT: {output}\nSTDERR: {error}"
    
    except Exception as e:
        error_str = f"Error: {e}"
        return error_str