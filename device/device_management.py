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
    "bluetooth" : ""
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
    # Define the dd command
    dd_command = [
        'sudo', 'dd', 'if=/dev/mmcblk0p3', f'of={tmp_dir_path}/deviceInfo.txt', 
        'bs=1', 'skip=2304', 'count=25'
    ]
    
    # Execute the dd command, redirecting stdout and stderr to /dev/null
    with open('/dev/null', 'w') as devnull:
        subprocess.run(dd_command, check=True, stdout=devnull, stderr=devnull)
    
    # Read the content of the output file
    with open('/unitree/tmp/deviceInfo.txt', 'r') as file:
        data = file.read().strip()
    
    # Parse the output data
    deviceInfo["sn"] = data[:16]
    deviceInfo["region"] = data[16:18]
    deviceInfo["hw"] = f"{data[18]}.{data[19]}"
    deviceInfo["bluetooth"] = data[20:]

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

def print_device_data():
    print(f"Serial: {get_real_serial_number()}")
    print(f"Model: Go2 {get_real_model()}")
    print(f"Region: {get_real_country()}")
    print(f"Package ver: {fetch_package_version()}")
    print(f"Hardware ver: {get_real_hw_ver()}")
    print(f"Bluetooth: {get_real_bluetooth_code()}")

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

def calculate_service_sha256(service_name):
    """Calculate the SHA-256 hash of a service file."""
    return get_file_sha256(services_path[service_name])

def is_firmware_version_supported():
    """Check if the current firmware version is supported for patching."""
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