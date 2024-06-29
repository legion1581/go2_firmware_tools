import time
from device_managment import *
from services import *
from constants import *
from dds_managment import *
import logging

# Configure basic logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Get the logger
logger = logging.getLogger('go2_firmware_tools')

logger.setLevel(logging.DEBUG)

def show_device_info():
    print(f"Serial: {fetch_real_serial_number()}")
    print(f"Model: {fetch_real_model()}")
    print(f"Region: {fetch_real_country()}")
    print(f"Package ver: {fetch_package_version()}")
    print(f"Hardware ver: {fetch_real_hw_ver()}")
    print(f"Bluetooth: {fetch_real_bluetooth_code()}")


def enable_secondary_dev():
    pass
    
    # model = input("Enter model (AIR/PRO/EDU): ")
    # desired_model = model.upper()

    # current_model = fetch_spoofed_model()

    # if desired_model not in model_name_to_id:
    #     raise ValueError(f"Invalid model specified: {desired_model}")

    # if desired_model == current_model:
    #     prompt = f"Already set to {desired_model}. Continue anyway (yes/[no])?"
    #     while True:
    #         user_input = input(prompt).strip().lower()
    #         # Check if the input is either "yes", empty (Enter pressed), or absent
    #         if user_input == "yes":
    #             logger.info("Continuing with model change...")
    #             break
    #         elif user_input in ["no", ""]:
    #             logger.info("Operation canceled by user.")
    #             return False
    #         else:
    #             logger.info("Invalid input. Please answer 'yes' or press Enter to continue, 'no' to cancel.")

    # stop_all_services()
    # install_service_patch("basic_service_check")
    # os.system(f"{services_path['basic_service_check']}")

    # real_model = fetch_real_model()
    # logger.info(f"Real model: {real_model}")

    # version_file_path = f"{basic_dir_path}/ver"
    # try:
    #     with open(version_file_path, 'r+') as file:
    #         current_ver_content = file.read().strip()
    #         new_model_number = model_name_to_id[desired_model]

    #         # Replace the last character with the new model number
    #         new_ver_content = current_ver_content[:-1] + str(new_model_number)

    #         # Write the new version back to the file
    #         file.seek(0)
    #         file.write(new_ver_content)
    #         file.truncate()
    #         logger.info(f"Model changed successfully from {current_model} to {desired_model} in version file.")
    # except FileNotFoundError:
    #     raise ValueError(f"Version file not found: {version_file_path}")
    #     return False
    # except Exception as e:
    #     raise ValueError(f"An error occurred while changing the device model: {str(e)}")
    #     return False

    # if real_model == "AIR":
    #     prompt = "AIR vui_service patch required. Install it now? ([yes]/no): "
    #     while True:
    #         user_input = input(prompt).strip().lower()
    #         if user_input in ["yes", ""]:
    #             create_file_with_content('/unitree/robot/basic/vuipower', b'\x00\x00')
    #             create_file_with_content('/unitree/robot/basic/vuivolume', b'\x00\x00')
    #             install_service_patch("vui_service", stop_service_flag=True)
    #             break
    #         elif user_input == "no":
    #             logger.info("Operation canceled by user.")
    #             return False
    #         else:
    #             logger.info("Invalid input. Please answer 'yes' or press Enter to continue, 'no' to cancel.")
    
    # prompt = "Reboot required, reboot now? ([yes]/no): "
    # while True:
    #     user_input = input(prompt).strip().lower()
    #     if user_input in ["yes", ""]:
    #         reboot_device()
    #     else:
    #         break

    # return True

def backup_partitions():

    pass

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
    
    prompt = "Reboot required, reboot now? ([yes]/no): "
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ["yes", ""]:
            reboot_device()
        else:
            break

    return True

def change_serial_number():
    serial_number = input("Enter new serial number: ")
    raise NotImplementedError

def change_system_sounds():
    source_path_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"media/audio")
    dest_path = '/unitree/module/audio_hub/audio_player/internal_corpus/Non_CN'
    copy_file(f"{source_path_base}/exit_companion_mode.mp3", f"{dest_path}/exit_companion_mode.mp3")
    copy_file(f"{source_path_base}/start_companion_mode.mp3", f"{dest_path}/start_companion_mode.mp3")
    copy_file(f"{source_path_base}/exit_obstacle_avoidance.mp3", f"{dest_path}/exit_obstacle_avoidance.mp3")
    copy_file(f"{source_path_base}/start_obstacle_avoidance.mp3", f"{dest_path}/start_obstacle_avoidance.mp3")
    dest_path = '/unitree/ota/engine/resource/prompt_tone/update/default'
    copy_file(f"{source_path_base}/begin.mp3", f"{dest_path}/begin.mp3")
    copy_file(f"{source_path_base}/end.mp3", f"{dest_path}/end.mp3")
    copy_file(f"{source_path_base}/failed.mp3", f"{dest_path}/failed.mp3")
    logger.info("Changing sounds complete")

def change_dds_domain_id():
    current_domain_id = load_config("config.json").get('domain_id', 'Not set')  # Fetch current domain ID
    print(f"Current DDS Domain: {current_domain_id}")
    new_domain_id = input("Enter new DDS Domain ID: ")
    try:
        new_domain_id = int(new_domain_id)  # Ensure that the input is converted to an integer
    except ValueError:
        logger.error("Invalid input: Domain ID must be an integer.")
        return

    current_fw_ver = fetch_package_version()
    if not is_firmware_version_supported():  # Ensure that current firmware version is checked
        logger.error(f"Firmware {current_fw_ver} is not supported")
        return

    if current_domain_id == new_domain_id:
        logger.info(f"Domain ID already set to: {new_domain_id}")
        return
    
    stop_all_services()

    # Process each file that needs patching according to the current firmware version
    for path, patch_type in dds_domain_patch_list[current_fw_ver].items():
        if patch_type == 'json_patch':
            dds_updade_domainid_json_file(path, new_domain_id)
        elif patch_type == 'yaml_patch':
            dds_update_domainid_yaml_file(path, new_domain_id)
        elif patch_type == 'python_patch':
            dds_update_domainid_python_file(path, new_domain_id)
        elif patch_type == 'service_hot_patch':
            offset = dds_domain_service_patch_offset[current_fw_ver].get(os.path.basename(path))
            if offset is not None:
                dds_update_domainid_hot_patch_file(path, offset, new_domain_id)
            else:
                logger.error(f"No offset found for hot patching the file: {path}")
    
    update_config("config.json", {'domain_id': new_domain_id})
    logger.info("DDS Domain ID updated successfully.")

    prompt = "Reboot required, reboot now? ([yes]/no): "
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ["yes", ""]:
            reboot_device()
        else:
            break


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
  
    prompt = "Reboot required, reboot now? ([yes]/no): "
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ["yes", ""]:
            reboot_device()
        else:
            break
    
    return True

def revert_service_to_factory():
    service_name = input("Enter service name: ")
    logger.info(f"Reverting to factory service: {service_name}")
    if service_name in service_list:
        install_factory_service(service_name, True)
    else:
        logger.error(f"Incorrect service name: {service_name}")

def revert_services_to_factory():
    install_factory_services()
    prompt = input("Reboot required, reboot now? ([yes]/no): ")
    user_input = input(prompt).strip().lower()
    prompt = "Reboot required, reboot now? ([yes]/no): "
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ["yes", ""]:
            reboot_device()
        else:
            break

def configure_interface_forwarding():
    raise NotImplementedError

def reboot_device():
    """Reboots the device by calling the operating system's reboot command."""
    try:
        logger.info("Attempting to reboot the device...")
        lay_down()
        os.system('reboot')
    except Exception as e:
        logger.error(f"An error occurred while trying to reboot the device: {e}")

def exit_program():
    print("Exiting...")
    exit()

def main():
    fetch_device_data()

    actions = {
        'Firmware': {
            1: show_device_info,
            2: enable_secondary_dev,
            3: backup_partitions
        },
        'DDS Settings': {
            4: change_dds_domain_id,
            5: change_dds_interface,
        },
        'Factory Settings': {
            6: revert_service_to_factory,
            7: revert_services_to_factory,
        },
        'Network Settings': {
            8: configure_interface_forwarding,
        },
        'System': {
            9: reboot_device,
            10: exit_program
        }
    }

    width = 80
    print('+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+'.center(width))
    print('|   GO2 Firmware TOOLS by legion1581            |'.center(width))
    print('|      https://theroboverse.com                 |'.center(width))
    print('+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+'.center(width))

    
    print("""
    Firmware:
        1: Show device info
        2: Enable secondary development
        3: Backup partitions
    DDS:
        4: Change DDS Domain ID
        5: Change DDS Interface (eth0/wlan1)
    Factory:
        6: Revert Single Service to Factory
        7: Revert All Services to Factory
    Network:
        8: Configure interface forwarding eth0 <--> wlan1
    System:
        9: Reboot device
        10: Exit
    """)

    try:
        choice = int(input("Select an option: "))
        for category, subactions in actions.items():
            if choice in subactions:
                subactions[choice]()
                break
        else:
            if choice == 10:
                print("Exiting...")
                return
            print("Invalid option, please try again.")
    except ValueError:
        print("Please enter a valid number.")


if __name__ == "__main__":
    main()
