import logging
import subprocess
from util.utilities import *
from .constants import service_list
from device.device_management import *

logger = logging.getLogger('go2_firmware_tools')

def is_patch_installed(service_name):
    """Check if a specific patch is already installed by comparing SHA-256 hashes."""
    current_ver = fetch_package_version()
    is_custom = is_custom_firmware()

    # Determine the expected SHA-256 hash from the services_sha dictionary
    version_key = '1.1.1' if is_custom else current_ver
    expected_sha = services_sha.get(version_key, {}).get("patched", {}).get(service_name)
    calculated_sha = calculate_service_sha256(service_name)

    return expected_sha == calculated_sha if expected_sha else False

def stop_service(service_name):
    if service_name == 'master_service':
        os.system(f"service {service_name} stop")
    else:
        # Run the command and suppress stdout and stderr
        subprocess.run(f"/unitree/sbin/mscli stopservice {service_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"{service_name} stopped")

def restart_service(service_name):
    # Run the command and suppress stdout and stderr
    subprocess.run(f"/unitree/sbin/mscli restartservice {service_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"{service_name} restarted")


def stop_all_services():
    print(f"Stopping all services...")
    # Order mirrors Install.CmdPreList from every official Unitree OTA package
    # (1.0.24 through 1.1.15): stop the high-level motion publishers BEFORE
    # calling basic_demarcate, otherwise the running controller keeps publishing
    # LowCmd and fights the lay-down move — the dog starts to squat and then
    # jumps as the controller applies a correction.
    #
    # mcf (Motion Control Framework, present since 1.1.6) is the active low-level
    # publisher on modern firmware when sport_mode is idle, so it must be in the
    # pre-lay-down set even though the stock OTA's CmdPreList omits it.
    # motion_switcher stays in post — it routes basic_demarcate's cmds to the
    # motors and has to remain up during the move.
    pre_lay_down = ("sport_mode", "advanced_sport", "ai_sport", "mcf")
    post_lay_down = ("motion_switcher",)
    for s in pre_lay_down:
        stop_service(s)
    lay_down()
    for s in post_lay_down:
        stop_service(s)
    already_stopped = set(pre_lay_down) | set(post_lay_down)
    for service in service_list:
        if service in already_stopped:
            continue
        stop_service(service)


def install_service_patch(service_name, stop_service_flag=False):
    """Install a service patch if the current firmware version is supported and the patch is not installed."""
    logger.info(f"Installing patch for {service_name}")
    if is_firmware_version_supported():
        if not is_patch_installed(service_name):
            current_package_ver = fetch_package_version()
            is_custom = is_custom_firmware()
            package_version = '1.1.1' if is_custom else current_package_ver
            # Get the directory containing main.py
            main_py_dir = get_script_path()

            # Construct the desired path
            source_path = os.path.join(main_py_dir, f"files/{package_version}/patched/{service_name}")
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
        current_package_ver = fetch_package_version()
        is_custom = is_custom_firmware()
        package_version = '1.1.1' if is_custom else current_package_ver

        main_py_dir = get_script_path()

        # Construct the desired path
        source_path = os.path.join(main_py_dir, f"files/{package_version}/factory/{service_name}")
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