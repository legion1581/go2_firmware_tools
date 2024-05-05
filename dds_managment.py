import os
import logging
import subprocess
import xml.etree.ElementTree as ET

logger = logging.getLogger('go2_firmware_tools')

def is_interface_up(interface):
    """Check if the specified network interface is up."""
    try:
        # Execute the command to get the status of the network interface
        result = subprocess.run(['ip', 'link', 'show', interface], capture_output=True, text=True)
        
        # Check if 'UP' is in the output which indicates the interface is up
        if 'state UP' in result.stdout:
            print(f"{interface} is up.")
            return True
        else:
            print(f"{interface} is down.")
            return False
    except subprocess.CalledProcessError:
        print(f"Failed to check status of {interface}.")
        return False

def cyclondds_xml_set(interface, config_name):

    cyclonedds_config_path = f"/unitree/etc/{config_name}"
    tree = ET.parse(cyclonedds_config_path)
    root = tree.getroot()

    # Find the NetworkInterface element and change its name attribute
    for network_interface in root.findall(".//NetworkInterface"):
        network_interface.set("name", interface)  # Change the interface name

    # Save the modified XML back to the file
    tree.write(cyclonedds_config_path)

        # Set the CYCLONEDDS_URI environment variable to point to the updated config file
    os.environ['CYCLONEDDS_URI'] = cyclonedds_config_path
    logger.debug(f"CYCLONEDDS_URI set to: {cyclonedds_config_path}")

    logger.info(f"DDS Domain configured with network interface {interface}")