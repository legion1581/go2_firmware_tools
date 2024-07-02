import os
import logging
import subprocess
from utilities import *
from constants import *

logger = logging.getLogger('go2_firmware_tools')

def lay_down():
    # os.system('/unitree/sbin/tscli release 0')
    os.system('/unitree/robot/tool/basic_demarcate Start_Move_zero_position')

deviceInfo = {
    "sn": "",
    "region":  "",
    "hw": "",
    "bluetooth" : ""
}

#  fetch real device info from uni.img
def fetch_device_data():
    # Define the dd command
    dd_command = [
        'dd', 'if=/dev/mmcblk0p3', f'of={tmp_dir_path}/deviceInfo.txt', 
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
    fetch_device_data()
    pass