import subprocess
import signal
import time
import logging
from utilities import *
from constants import *
from device_managment import *

logger = logging.getLogger('go2_firmware_tools')

def is_patch_installed(service_name):
    """Check if a specific patch is already installed by comparing SHA-256 hashes."""
    current_ver = fetch_package_version()
    expected_sha = services_sha.get(current_ver, {}).get("patched", {}).get(service_name)
    calculated_sha = calculate_service_sha256(service_name)
    return expected_sha == calculated_sha if expected_sha else False

def stop_service(service_name):
    if service_name == 'master_service':
        os.system(f"service {service_name} stop")
    else:
        os.system(f"/unitree/sbin/mscli stopservice {service_name}")
    
    logger.info(f"{service_name} stopped")


def stop_all_services():
    logger.info(f"Stopping all services...")
    lay_down()
    for service in service_list:
        stop_service(service)


def install_service_patch(service_name):
    """Install a service patch if the current firmware version is supported and the patch is not installed."""
    logger.info(f"Installing patch for {service_name}")
    if is_firmware_version_supported():
        if not is_patch_installed(service_name):
            create_directory(tmp_dir_path)
            package_version = fetch_package_version()
            source_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"services/{package_version}/patched/{service_name}")
            dest_path = services_path[service_name]
            copy_file(source_path, dest_path)
            change_file_permissions(source_path, 0o775)
            logger.info(f"Patch installed for {service_name}")
        else:
            logger.info(f"Patch already installed for {service_name}")
    else:
        raise ValueError("Firmware version is not supported")

def install_factory_service(service_name):
    """Install a service patch if the current firmware version is supported and the patch is not installed."""
    if is_firmware_version_supported():
        package_version = fetch_package_version()
        source_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"services/{package_version}/factory/{service_name}")
        dest_path = services_path[service_name]
        copy_file(source_path, dest_path)
        change_file_permissions(dest_path, 0o775)
        logger.info(f"Factory service installed for {service_name}")
    else:
        raise ValueError("Firmware version is not supported")


def install_factory_services():
    stop_all_services()
    for service in services_path.keys():
            install_factory_service(service)
    logger.info("Please reboot for changes to take effect.")

if __name__ == "__main__":
    stop_all_services()