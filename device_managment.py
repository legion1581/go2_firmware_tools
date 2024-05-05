import os
import logging
from utilities import *
from constants import *

logger = logging.getLogger('go2_firmware_tools')

def lay_down():
    os.system('/unitree/sbin/tscli release 0')

def fetch_real_serial_number():
    """Read the real serial number from its expected directory."""
    return read_str_from_file(f"{tmp_dir_path}/code")

def fetch_spoofed_serial_number():
    """Read a spoofed serial number from a temporary directory."""
    return read_str_from_file(f"{basic_dir_path}/code")

def fetch_real_model():
    """Retrieve the model type from the version file in the basic directory."""
    version = read_str_from_file(f"{tmp_dir_path}/ver")
    if version:
        model_number = int(version[-1])
        return model_id_to_name.get(model_number, None)
    return None

def fetch_spoofed_model():
    """Retrieve the model type from the version file in the tmp directory."""
    version = read_str_from_file(f"{basic_dir_path}/ver")
    if version:
        model_number = int(version[-1])
        return model_id_to_name.get(model_number, None)
    return None

def fetch_real_country():
    """Get the country code from the version file in the basic directory."""
    return read_str_from_file(f"{tmp_dir_path}/country")

def fetch_spoofed_country():
    """Get the country code from the version file in the tmp directory."""
    return read_str_from_file(f"{basic_dir_path}/country")

def fetch_package_version():
    """Read the package version from a JSON file."""
    package_info = read_json_file('/unitree/robot/pkg/version/version.json')
    return package_info.get('Package', 'Version not found') if package_info else 'Version not found'

def calculate_service_sha256(service_name):
    """Calculate the SHA-256 hash of a service file."""
    return get_file_sha256(services_path[service_name])

def is_firmware_version_supported():
    """Check if the current firmware version is supported for patching."""
    return fetch_package_version() in services_sha

if __name__ == "__main__":
    pass