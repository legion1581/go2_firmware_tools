import logging
import subprocess
from util.utilities import *
from .constants import service_list
from device.device_management import *

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
        # Run the command and suppress stdout and stderr
        subprocess.run(f"/unitree/sbin/mscli stopservice {service_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"{service_name} stopped")


def stop_all_services():
    print(f"Stopping all services...")
    stop_service("sport_mode")
    stop_service("advanced_sport")
    stop_service("ai_sport")
    lay_down()
    for service in service_list:
        stop_service(service)


def install_service_patch(service_name, stop_service_flag=False):
    """Install a service patch if the current firmware version is supported and the patch is not installed."""
    logger.info(f"Installing patch for {service_name}")
    if is_firmware_version_supported():
        if not is_patch_installed(service_name):
            package_version = fetch_package_version()
            # Get the directory containing main.py
            main_py_dir = get_script_path()

            # Construct the desired path
            source_path = os.path.join(main_py_dir, f"services/{package_version}/patched/{service_name}")
            dest_path = services_path[service_name]
            if stop_service_flag:
                stop_service(service_name)
            copy_file(source_path, dest_path)
            change_file_permissions(dest_path, 0o775)
            print(f"Patch installed for {service_name}")
        else:
            print(f"Patch already installed for {service_name}")
    else:
        raise ValueError("Firmware version is not supported")

def install_factory_service(service_name, stop_service_flag=False):
    """Install a service patch if the current firmware version is supported and the patch is not installed."""
    if is_firmware_version_supported():
        package_version = fetch_package_version()
        main_py_dir = get_script_path()

        # Construct the desired path
        source_path = os.path.join(main_py_dir, f"services/{package_version}/factory/{service_name}")
        dest_path = services_path[service_name]
        if stop_service_flag:
                stop_service(service_name)
        copy_file(source_path, dest_path)
        change_file_permissions(dest_path, 0o775)
        print(f"Factory service installed for {service_name}")
    else:
        raise ValueError("Firmware version is not supported")


def install_factory_services():
    stop_all_services()
    for service in services_path.keys():
            install_factory_service(service)

if __name__ == "__main__":
    stop_all_services()