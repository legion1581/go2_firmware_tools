from InquirerPy import inquirer
import os
import logging
from util.utilities import run_shell_command, file_exists, copy_file, change_file_permissions
from device import device_management
from device.device_services import stop_all_services

# Get the logger
logger = logging.getLogger('go2_firmware_tools')

def update_mcu_firmware():
    """
    Updates the MCU firmware by stopping all services, locating the flasher tool,
    and running the upgrade command.
    """
    try:   
        # Define source and destination paths
        source_path_1 = os.path.abspath('firmware/mcu/McuBoot')
        source_path_2 = os.path.abspath('firmware/mcu/AppPublic.bin')
        dest_path_1 = '/unitree/robot/tool/boot/McuBoot'
        dest_path_2 = '/unitree/robot/tool/boot/AppPublic.bin'

        # Step 1: Verify that Flasher files exist, if not copy them
        if not file_exists(dest_path_1):
            print(f"{dest_path_1} not found. Copying from {source_path_1}...")
            copy_file(source_path_1, dest_path_1)
            change_file_permissions(dest_path_1, 0o775)

        if not file_exists(dest_path_2):
            print(f"{dest_path_2} not found. Copying from {source_path_2}...")
            copy_file(source_path_2, dest_path_2)

        # Step 2: Stop all services
        stop_all_services()

        # Step 3: Run the shell command to start the MCU upgrade
        print("Starting MCU firmware upgrade...")
        run_shell_command(f'{source_path_1} start_Mcu_Upgrade', suppress_empty_output=False)

        print("MCU firmware update completed successfully.")

        # Step 4: Prompt for reboot
        prompt = "Reboot required, reboot now? ([yes]/no): "
        while True:
            user_input = input(prompt).strip().lower()
            if user_input in ["yes", ""]:
                device_management.reboot_device()
                break
            elif user_input == "no":
                break
            else:
                logger.info("Invalid input. Please answer 'yes' or press Enter to continue, 'no' to cancel.")

    except Exception as e:
        print(f"An error occurred during MCU firmware update: {e}")

# 
# CMD MENU
#    

def display_mcu_firmware_menu():
    menu_items = [
        'Update MCU firmware (1.1.1+ firmware)',
        'Back to Main Menu',
        'Quit'
    ]
     
    choice = inquirer.select(
        message="Select an option:",
        choices=menu_items
    ).execute()

    return choice

def handle_mcu_firmware_choice(choice):
    if choice == 'Update MCU firmware (1.1.1+ firmware)':
        update_mcu_firmware()
    elif choice == 'Back to Main Menu':
        return False
    elif choice == 'Quit':
        exit()
    else:
        print(f"Invalid choice, please try again. choice : {choice}")
    return True

def cli_handler():
    while True:
        choice = display_mcu_firmware_menu()
        if not handle_mcu_firmware_choice(choice):
            break