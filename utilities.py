import os
import shutil
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

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
        logger.error(f"Unable to copy file: {e}")

def replace_file(src, dst):
    """Replace one file with another."""
    try:
        shutil.move(src, dst)
        logger.info(f"Replaced {src} with {dst}")
    except Exception as e:
        logger.error(f"Error replacing file: {e}")

def read_str_from_file(file_path):
    """Read and return content of a file, stripping whitespace."""
    try:
        with open(file_path, 'r') as file:
            content = file.read().strip()
        return content
    except FileNotFoundError:
        logger.info(f"File not found: {file_path}")
        return None
    except Exception as e:
        logger.error(f"An error occurred reading {file_path}: {e}")
        return None

def get_file_sha256(file_path):
    """Calculate the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        logger.info(f"File not found: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error computing SHA-256 for file {file_path}: {e}")
        return None

def read_json_file(file_path):
    """Read JSON file and return its content."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON content in {file_path}.")
    except Exception as e:
        logger.error(f"An error occurred reading JSON from {file_path}: {e}")
    return None

def change_file_permissions(file_path, mode):
    """Changes the permissions of a file to the given mode.

    Args:
        file_path (str): The path to the file.
        mode (int): The permission mode to set, in octal notation (e.g., 0o644).
    """
    try:
        os.chmod(file_path, mode)
        logging.info(f"Permissions changed for {file_path} to {oct(mode)}")
    except FileNotFoundError:
        logging.error(f"The file {file_path} does not exist.")
    except PermissionError:
        logging.error(f"Permission denied when trying to change the permissions of {file_path}.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
