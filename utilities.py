import os
import shutil
import hashlib
import json
import logging

logger = logging.getLogger('go2_firmware_tools')

def file_exists(file_path):
    return os.path.exists(file_path)

def create_directory(path):
    """Create a directory if it does not exist."""
    os.makedirs(path, exist_ok=True)
    logger.info(f"Directory ensured: {path}")

def copy_file(source_path, destination_path):
    """Copy the contents of one file to another."""
    try:
        shutil.copy(source_path, destination_path)
        logger.info(f"File copied from {source_path} to {destination_path}")
    except IOError as e:
        raise SystemError(f"Unable to copy file: {e}")

def read_str_from_file(file_path):
    """Read and return content of a file, stripping whitespace."""
    try:
        with open(file_path, 'r') as file:
            content = file.read().strip()
        return content
    except FileNotFoundError:
        logger.info(f"File not found: {file_path}")
    except Exception as e:
        raise SystemError(f"An error occurred reading {file_path}: {e}")
    
def create_file_with_content(file_path, content):
    """
    Create a file with specified content.

    Args:
    file_path (str): The path where the file will be created.
    content (bytes): The content to write to the file.
    """
    try:
        with open(file_path, 'wb') as file:
            file.write(content)
        logger.info(f"File created at {file_path} with specified content.")
    except Exception as e:
        raise SystemError(f"Failed to create file: {e}")

def get_file_sha256(file_path):
    """Calculate the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        raise SystemError(f"File not found: {file_path}")
        return None
    except Exception as e:
        raise SystemError(f"Error computing SHA-256 for file {file_path}: {e}")
        return None

def read_json_file(file_path):
    """Read JSON file and return its content."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise SystemError(f"File not found: {file_path}")
    except json.JSONDecodeError:
        raise SystemError(f"Invalid JSON content in {file_path}.")
    except Exception as e:
        raise SystemError(f"An error occurred reading JSON from {file_path}: {e}")
    return None

def change_file_permissions(file_path, mode):
    """Changes the permissions of a file to the given mode.

    Args:
        file_path (str): The path to the file.
        mode (int): The permission mode to set, in octal notation (e.g., 0o644).
    """
    try:
        os.chmod(file_path, mode)
        logger.info(f"Permissions changed for {file_path} to {oct(mode)}")
    except FileNotFoundError:
        raise SystemError(f"The file {file_path} does not exist.")
    except PermissionError:
        raise SystemError(f"Permission denied when trying to change the permissions of {file_path}.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise SystemError(f"An unexpected error occurred: {e}")

def load_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def update_config(file_path, updates):
    config = load_config(file_path)
    config.update(updates)
    with open(file_path, 'w') as file:
        json.dump(config, file, indent=4)


if __name__ == "__main__":
    target_directory = '/home/legion/Documents/theroboverse/go2_firmware_tools/services/1.0.24/patched/vui_service'  # Change this to your target directory
    print(get_file_sha256(target_directory))