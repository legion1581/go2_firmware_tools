import time
from device_managment import *
from services import *
from constants import *
from dds_managment import *
import logging

logger = logging.getLogger('go2_firmware_tools')

# Set the logging level
logger.setLevel(logging.DEBUG)  # This will capture all levels from DEBUG and above

# Create handlers that will handle the log messages
stream_handler = logging.StreamHandler()  # To output log messages to the console

# Optionally set a formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)

# Set a specific level on the handler if needed
stream_handler.setLevel(logging.DEBUG)  # This will capture all levels from DEBUG and above

# Add the handler to the logger
logger.addHandler(stream_handler)

def change_model():
    model = input("Enter model (AIR/PRO/EDU): ")
    desired_model = model.upper()
    if desired_model not in model_name_to_id:
        raise ValueError(f"Invalid model specified: {desired_model}")

    current_model = fetch_spoofed_model()

    if desired_model == current_model:
        logger.info(f"Already set to {desired_model}")
        return True

    stop_all_services()
    install_service_patch("basic_service_check")
    os.system(f"{services_path['basic_service_check']}")
    
    real_model = fetch_real_model()
    
    logger.info(f"Current spoofed model: {current_model}")
    logger.info(f"Real model: {real_model}")

    version_file_path = f"{basic_dir_path}/ver"
    try:
        with open(version_file_path, 'r+') as file:
            current_ver_content = file.read().strip()
            new_model_number = model_name_to_id[desired_model]

            # Replace the last character with the new model number
            new_ver_content = current_ver_content[:-1] + str(new_model_number)

            # Write the new version back to the file
            file.seek(0)
            file.write(new_ver_content)
            file.truncate()
            logger.info(f"Model changed successfully from {current_model} to {desired_model} in version file.")
    except FileNotFoundError:
        raise ValueError(f"Version file not found: {version_file_path}")
        return False
    except Exception as e:
        raise ValueError(f"An error occurred while changing the device model: {str(e)}")
        return False

    if real_model == "AIR":
        choice = input("AIR vui_service patch required. Install it now? (yes/no): ")
        if choice.lower() == 'yes':
            install_service_patch("vui_service")
    
    choice = input("Reboot required, reboot now? (yes/no): ")
    if choice.lower() == 'yes':
        reboot_device()

    return True


def change_region():
    region = input("Enter region: ")
    desired_region = region.upper()
    if desired_region not in common_regions:
        raise ValueError(f"Invalid region specified: {desired_region}")

    current_region = fetch_spoofed_country()

    if desired_region == current_region:
        logger.info(f"Already set to {desired_region}")
        return True

    stop_all_services()
    install_service_patch("basic_service_check")
    os.system(f"{services_path['basic_service_check']}")
    
    real_region = fetch_real_country()
    
    logger.info(f"Current spoofed region: {current_region}")
    logger.info(f"Real model: {real_region}")

    country_file_path = f"{basic_dir_path}/country"
    try:
        with open(country_file_path, 'r+') as file:
            country_file_path = file.read().strip()

            # Write the new version back to the file
            file.seek(0)
            file.write(desired_region)
            file.truncate()
            logger.info(f"Region changed successfully from {current_region} to {desired_region} in version file.")
    except FileNotFoundError:
        raise ValueError(f"Country file not found: {country_file_path}")
        return False
    except Exception as e:
        raise ValueError(f"An error occurred while changing the device region: {str(e)}")
        return False
    
    choice = input("Reboot required, reboot now? (yes/no): ")
    if choice.lower() == 'yes':
        reboot_device()

    return True

def change_serial_number():
    serial_number = input("Enter new serial number: ")
    raise NotImplementedError

def change_dds_domain_id():
    domain_id = input("Enter new DDS Domain ID: ")
    raise NotImplementedError

def change_dds_interface():
    interface = input("Enter new interface (eth0/wlan1): ")
    logger.info(f"Changing the DDS network config to {interface}")
    if interface not in interface_list:
        logger.error(f"Invalid interface specified: {interface}")
        return
    
    if not is_interface_up(interface):
        logger.error(f"Interface {interface} is DOWN")
        return
    
    stop_all_services()
    install_service_patch("master_service")

    cyclondds_xml_set(interface, 'cyclonedds.xml')
    cyclondds_xml_set(interface, 'cyclonedds_noshm.xml')
    logger.info(f"DDS Interface changed to {interface}")
  
    choice = input("Reboot required, reboot now? (yes/no): ")
    if choice.lower() == 'yes':
        reboot_device()
    
    return True

def revert_service_to_factory():
    service_name = input("Enter service name: ")
    logger.info(f"Reverting to factory service: {service_name}")
    if service_name in service_list:
        install_factory_service(service_name)
    else:
        logger.error(f"Incorrect service name: {service_name}")

def revert_services_to_factory():
    install_factory_services()

def reboot_device():
    """Reboots the device by calling the operating system's reboot command."""
    try:
        logger.info("Attempting to reboot the device...")
        lay_down()
        os.system('reboot')
    except Exception as e:
        logger.error(f"An error occurred while trying to reboot the device: {e}")

def main():
    actions = {
        1: change_model,
        2: change_region,
        3: change_serial_number,
        4: change_dds_domain_id,
        5: change_dds_interface,
        6: revert_service_to_factory,
        7: revert_services_to_factory,
        8: reboot_device
    }

    print('+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+')
    print('|   GO2 Firmware TOOLS by legion1581    |')
    print('|      https://theroboverse.com         |')
    print('+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+')
   
    print(""" 
    1: Spoof Model (AIR/PRO/EDU)
    2: Spoof Region (US/CN/JP/DE/IN/FR/UK/BR/RU/CA/IT/ES/AU/MX/KR/ID/TR/SA/NL/CH)
    3: Spoof SN
    4: Change DDS Domain ID
    5: Change DDS Interface (eth0/wlan1)
    6: Revert Single Service to Factory    
    7: Revert All Services to Factory
    8: Reboot device
    9: Exit
    """)
    try:
        choice = int(input("Select an option: "))
        if choice == 9:
            print("Exiting...")
            exit
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid option, please try again.")
    except ValueError:
        print("Please enter a valid number.")

if __name__ == "__main__":
    main()
