import os
import logging
import subprocess
from util.utilities import *
from .constants import tmp_dir_path, model_id_to_name, services_sha, services_path, basic_dir_path

logger = logging.getLogger('go2_firmware_tools')

deviceInfo = {
    "sn": "",
    "region":  "",
    "hw": "",
    "bluetooth" : "",
    "secure_boot": False
}

script_path = ''

def device_init(script_path_l):
    fetch_device_data()
    script_path = script_path_l

def lay_down():
    # os.system('/unitree/sbin/tscli release 0')
    os.system('/unitree/robot/tool/basic_demarcate Start_Move_zero_position')


#  fetch real device info from uni.img
def fetch_device_data():

    os.makedirs(tmp_dir_path, exist_ok=True)

    # Define the dd command to read data from uni.img
    dd_command = [
        'dd', 'if=/dev/mmcblk0p3', f'of={tmp_dir_path}/deviceInfo.txt', 
        'bs=1', 'skip=2304', 'count=25'
    ]
    
    # Execute the dd command, redirecting stdout and stderr to /dev/null
    with open('/dev/null', 'w') as devnull:
        subprocess.run(dd_command, check=True, stdout=devnull, stderr=devnull)
    
    # Read the content of the output file
    with open('/unitree/tmp/deviceInfo.txt', 'r') as file:
        uni_data = file.read().strip()
    
    # Parse the output data
    deviceInfo["sn"] = uni_data[:16]
    deviceInfo["region"] = uni_data[16:18]
    deviceInfo["hw"] = f"{uni_data[18]}.{uni_data[19]}"
    deviceInfo["bluetooth"] = uni_data[20:]

    # Lets read the first sector after 0x40 to verify if we have Secure Boot or not
    # Define the dd command to read data from preloader
    dd_command = [
        'dd', 'if=/dev/mmcblk0', f'of={tmp_dir_path}/preloader_first_sector.txt', 
        'bs=512', 'skip=64', 'count=1'
    ]
    
    # Execute the dd command, redirecting stdout and stderr to /dev/null
    with open('/dev/null', 'w') as devnull:
        subprocess.run(dd_command, check=True, stdout=devnull, stderr=devnull)
    
    # Read the content of the output file
    with open('/unitree/tmp/preloader_first_sector.txt', 'rb') as file:
        preloader_data = file.read()

    deviceInfo["secure_boot"] = preloader_data[:4] == b'RKSS'

    return deviceInfo

def get_real_serial_number():
    """Read the real serial number"""
    return deviceInfo["sn"]

def get_real_model():
    """Retrieve the model type from the version file in the basic directory."""
    model_number = int(deviceInfo["sn"][4]) # get the 5th number from the sn
    return model_id_to_name.get(model_number, None) 

def get_real_country():
    """Get the country code from the version file in the basic directory."""
    return deviceInfo["region"]

def get_real_hw_ver():
    return deviceInfo["hw"]

def get_real_bluetooth_code():
    return deviceInfo["bluetooth"]

def get_secure_boot_status():
    return deviceInfo["secure_boot"]

def print_device_data():
    """Print device-related information."""
    print(f"Serial: {get_real_serial_number()}")
    print(f"Model: Go2 {get_real_model()}")
    print(f"Region: {get_real_country()}")

    # Fetch custom package version and determine the final package version string
    custom_package_version = fetch_custom_package_version()
    if custom_package_version:  # Check if custom_package_version is not None or empty
        package_version = f"{fetch_package_version()} mod {custom_package_version}"
    else:
        package_version = fetch_package_version()

    print(f"Package ver: {package_version}")
    print(f"Hardware ver: {get_real_hw_ver()}")
    print(f"Bluetooth: {get_real_bluetooth_code()}")
    print("Secure Boot: " + ("ENABLED" if get_secure_boot_status() else "DISABLED"))

def get_spoofed_model():
    """Retrieve the model type from the version file in the basic directory."""
    version = read_str_from_file(f"{basic_dir_path}/ver")
    if version:
        model_number = int(version[-1])
        return model_id_to_name.get(model_number, None)
    return None

def fetch_package_version():
    """Read the package version from a JSON file."""
    package_info = read_json_file('/unitree/robot/pkg/version/version.json')
    return package_info.get('Package', 'Version not found') if package_info else 'Version not found'

def fetch_custom_package_version():
    """
    Read the Mod version from a JSON file.
    Returns the version if 'Mod' exists, otherwise returns None.
    """
    package_info = read_json_file('/unitree/robot/pkg/version/version.json')
    if package_info and 'Mod' in package_info:
        return package_info['Mod']
    return None

def is_custom_firmware():
    """Read the package version from a JSON file."""
    package_info = read_json_file('/unitree/robot/pkg/version/version.json')
    return 'Mod' in package_info

def calculate_service_sha256(service_name):
    """Calculate the SHA-256 hash of a service file."""
    return get_file_sha256(services_path[service_name])

def is_firmware_version_supported():
    """Check if the current firmware version is supported for patching."""
    if is_custom_firmware():
        return True
    else:
        return fetch_package_version() in services_sha

def reboot_device():
    """Reboots the device by calling the operating system's reboot command."""
    try:
        print("Attempting to reboot the device...")
        lay_down()
        os.system('reboot')
    except Exception as e:
        logger.error(f"An error occurred while trying to reboot the device: {e}")

def get_script_path():
    return script_path

if __name__ == "__main__":
    fetch_device_data()
    pass