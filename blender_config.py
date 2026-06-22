import platform
import os

def get_blender_path():
    system = platform.system()

    if system == "Windows":
        # Common Windows install paths - checks both, uses whichever exists
        possible_paths = [
            r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        # If none found, return default and user can edit manually
        return r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

    elif system == "Darwin":  # Mac
        return "/Applications/Blender.app/Contents/MacOS/Blender"

    elif system == "Linux":
        return "/usr/bin/blender"

    else:
        raise Exception(f"Unsupported OS: {system}")


def get_output_folder():
    # Always points to the 'outputs' folder inside this project
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir