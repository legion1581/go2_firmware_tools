import logging
from utilities import *
from constants import *

logger = logging.getLogger(__name__)

def fetch_real_serial_number():
    """Read the real serial number from its expected directory."""
    return read_str_from_file(f"{basic_dir_path}/code")

def fetch_spoofed_serial_number():
    """Read a spoofed serial number from a temporary directory."""
    return read_str_from_file(f"{tmp_dir_path}/code")

def fetch_real_model():
    """Retrieve the model type from the version file in the basic directory."""
    version = read_str_from_file(f"{basic_dir_path}/ver")
    if version:
        model_number = int(version[-1])
        return go2_models.get(model_number, None)
    return None

def fetch_spoofed_model():
    """Retrieve the model type from the version file in the tmp directory."""
    version = read_str_from_file(f"{tmp_dir_path}/ver")
    if version:
        model_number = int(version[-1])
        return go2_models.get(model_number, None)
    return None

def fetch_real_country():
    """Get the country code from the version file in the basic directory."""
    return read_str_from_file(f"{basic_dir_path}/country")

def fetch_spoofed_country():
    """Get the country code from the version file in the tmp directory."""
    return read_str_from_file(f"{tmp_dir_path}/country")

def fetch_package_version():
    """Read the package version from a JSON file."""
    package_info = read_json_file('unitree/robot/pkg/version/version.json')
    return package_info.get('Package', 'Version not found') if package_info else 'Version not found'

def calculate_service_sha256(service_name):
    """Calculate the SHA-256 hash of a service file."""
    return get_file_sha256(services_path[service_name])

def is_firmware_version_supported():
    """Check if the current firmware version is supported for patching."""
    return fetch_package_version() in services_sha

def is_patch_installed(service_name):
    """Check if a specific patch is already installed by comparing SHA-256 hashes."""
    current_ver = fetch_package_version()
    expected_sha = services_sha.get(current_ver, {}).get("patched", {}).get(service_name)
    calculated_sha = calculate_service_sha256(service_name)
    return expected_sha == calculated_sha if expected_sha else False

def install_service_patch(service_name):
    """Install a service patch if the current firmware version is supported and the patch is not installed."""
    if is_firmware_version_supported():
        if not is_patch_installed(service_name):
            create_directory(tmp_dir_path)
            package_version = fetch_package_version()
            replace_file(f"patched/{package_version}/{service_name}", services_path[service_name])
            change_file_permissions(f"patched/{package_version}/{service_name}", 0o775)
            logger.info(f"Patch installed for {service_name}")
        else:
            logger.info(f"Patch already installed for {service_name}")

def install_all_patches():
    """Install patches for all services defined in constants."""
    if file_exists(f"{basic_dir_path}/code") and\
        file_exists(f"{basic_dir_path}/ver") and\
        file_exists(f"{basic_dir_path}/country"):
        
        for service in services_path.keys():
            install_service_patch(service)

        logger.info("Please reboot for changes to take effect.")
    else:
        logger.error(f"Some files in {basic_dir_path} are missing, can not proceed futher")

def change_device_model(desired_model):
    desired_model = desired_model.upper()
    if desired_model not in go2_models:
        logger.error(f"Invalid model specified: {desired_model}")
        return False

    real_model = fetch_real_model()
    current_model = fetch_spoofed_model()

    if desired_model == current_model:
        logger.info(f"Already set to {desired_model}")
        return True
    
    logger.info(f"Current spoofed model: {current_model}")
    logger.info(f"Real model: {real_model}")

    version_file_path = f"{basic_dir_path}/ver"
    try:
        with open(version_file_path, 'r+') as file:
            current_version = file.read().strip()
            new_model_number = go2_models[desired_model]

            # Replace the last character with the new model number
            new_version = current_version[:-1] + new_model_number

            # Write the new version back to the file
            file.seek(0)
            file.write(new_version)
            file.truncate()
            logger.info(f"Model changed successfully from {current_model} to {desired_model} in version file.")
            logger.info("Please reboot for changes to take effect.")
            return True
    except FileNotFoundError:
        logger.error(f"Version file not found: {version_file_path}")
        return False
    except Exception as e:
        logger.error(f"An error occurred while changing the device model: {str(e)}")
        return False




def main():
    print(get_file_sha256('/home/legion/Documents/theroboverse/go2_firmware_tools/patched/1.0.23/vui_service'))

if __name__ == "__main__":
    main()