import os
import json
import yaml
import logging
import subprocess
import xml.etree.ElementTree as ET
from keystone import *
from constants import *

logger = logging.getLogger('go2_firmware_tools')

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
# logger = logging.getLogger(__name__)


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

def dds_updade_domainid_json_file(file_path, new_domain_id):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Update DomainId in the nested dictionary
        if "DdsParameter" in data:
            data['DdsParameter']['Participant']['DomainId'] = new_domain_id
        else:
            data['Participant']['DomainId'] = new_domain_id

        # Write the modified data back to the file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

        logger.info(f"Updated DomainId in {file_path} to {new_domain_id}")
    except json.JSONDecodeError:
        raise ValueError(f"Error: {file_path} does not contain valid JSON.")
    except FileNotFoundError:
        raise SystemError(f"Error: {file_path} not found.")
    except Exception as e:
        raise SystemError(f"An unexpected error occurred: {str(e)}")

def dds_update_domainid_python_file(file_path, new_domain_id):
    try:
        # Read the content of the file
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Update the line containing the DomainParticipant
        with open(file_path, 'w') as file:
            for line in lines:
                if "domainParticipant = DomainParticipant(" in line:
                    # Replace the line with the new Domain ID
                    line = f"domainParticipant = DomainParticipant({new_domain_id})\n" 
                file.write(line)

        logger.info(f"Updated DomainParticipant in {file_path} to {new_domain_id}")

    except FileNotFoundError:
        raise SystemError(f"Error: {file_path} not found.")
    except Exception as e:
        raise SystemError(f"An unexpected error occurred: {str(e)}")
    
def dds_update_domainid_yaml_file(file_path, new_domain_id):
    try:
        # Load the YAML file, replacing tabs with spaces
        with open(file_path, 'r') as file:
            file_content = file.read().replace('\t', '    ')  # Replace tabs with four spaces
            data = yaml.safe_load(file_content)

        # Update the domain_id
        if 'dds' in data and 'domain_id' in data['dds']:
            data['dds']['domain_id'] = new_domain_id
            # Write the updated data back to the YAML file
            with open(file_path, 'w') as file:
                yaml.safe_dump(data, file, default_flow_style=False)
            
            logger.info(f"Updated domain_id in {file_path} to {new_domain_id}")
        else:
            logger.info("The 'domain_id' key was not found in the specified path within the YAML structure.")

    except FileNotFoundError:
        raise SystemError(f"Error: {file_path} not found.")
    except yaml.YAMLError as e:
        raise SystemError(f"Error processing YAML file: {str(e)}")
    except Exception as e:
        raise SystemError(f"An unexpected error occurred: {str(e)}")



def dds_update_domainid_hot_patch_file(file_path, offset, new_domain_id):
    logger.info(f"Patching file: {file_path} with domainid: {new_domain_id}")
    # Ensure new_domain_id is within a valid range for a 16-bit unsigned integer
    if not (0 <= new_domain_id < 65535):  
        logger.error("Invalid domain ID provided. It must be between 0 and 65535")
        return

    # Assemble the instruction to move the new domain ID into the 32-bit register w0
    instruction = f"mov w0, #{new_domain_id}"
    ks = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)
    
    try:
        encoding, count = ks.asm(instruction)
        new_instruction = bytes(encoding)
        if len(new_instruction) != 4:  # Ensure the new instruction has the correct byte length
            logger.error(f"Unexpected instruction length: {len(new_instruction)}")
            return
    except KsError as e:
        logger.error(f"Error assembling the instruction: {e}")
        return

    logger.debug(f"New instruction: {[f'0x{byte:02x}' for byte in new_instruction]}")

    # Read the existing binary data
    try:
        with open(file_path, 'rb') as file:
            binary_data = bytearray(file.read())
    except IOError as e:
        logger.error(f"Error reading the file: {e}")
        return

    logger.debug(f"Current data: {[f'0x{byte:02x}' for byte in binary_data[offset:offset + len(new_instruction)] if len(new_instruction)]}")
    # Patch the binary data at the specified offset
    binary_data[offset:offset + len(new_instruction)] = new_instruction


    # Write the modified binary data back to the file
    try:
        with open(file_path, 'wb') as file:
            file.write(binary_data)
        logger.info("Binary file patched successfully.")
    except IOError as e:
        logger.error(f"Error writing to the file: {e}")

if __name__ == "__main__":
    dds_update_domainid_hot_patch_file('/unitree/module/audio_hub/audiohub', 0x69ec, 123)
