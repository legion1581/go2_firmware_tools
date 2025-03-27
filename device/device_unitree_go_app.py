import logging
import os
from InquirerPy import inquirer
from .device_management import get_script_path
from util.utilities import copy_file,change_file_permissions,get_latest_ota_version_info, run_shell_command

def enable_unitree_go_app_compatibility():
    """
    Enables compatibility with the latest Unitree Go App by updating the version script.
    """
    # Fetch the latest OTA version information
    latest_ver = get_latest_ota_version_info()

    # Construct the shell command to update the version script
    command = f"echo \"echo '{latest_ver}'\" > /unitree/module/bashrunner/content_acquisition/get_whole_packet_version.sh"
    run_shell_command(command)
    print(f"Enabled Unitree Go App compatibility with version: {latest_ver}")


def disable_unitree_go_app_compatibility():
    """
    Disables compatibility with the Unitree Go App by restoring the original version script.
    """
    # Get the script directory and package version
    main_py_dir = get_script_path()

    # Construct the source and destination paths
    source_path = os.path.join(main_py_dir, f"files/get_whole_packet_version.sh")
    dest_path = '/unitree/module/bashrunner/content_acquisition/get_whole_packet_version.sh'

    # Copy the file and set permissions
    copy_file(source_path, dest_path)
    change_file_permissions(dest_path, 0o644)

    print("Disabled Unitree Go App compatibility")

# 
# CMD MENU
#    

def display_device_unitree_go_app_menu():
    menu_items = [
        'Enable Latest Unitree Go App Compatibility',
        'Disable Latest Unitree Go App Compatibility',
        'Back to Main Menu',
        'Quit'
    ]
     
    choice = inquirer.select(
        message="Select an option:",
        choices=menu_items
    ).execute()

    return choice

def handle_device_unitree_go_app_choice(choice):
    if choice == 'Enable Latest Unitree Go App Compatibility':
        enable_unitree_go_app_compatibility()
    elif choice == 'Disable Latest Unitree Go App Compatibility':
        disable_unitree_go_app_compatibility()
    elif choice == 'Back to Main Menu':
        return False
    elif choice == 'Quit':
        exit()
    else:
        print(f"Invalid choice, please try again. choice : {choice}")
    return True

def cli_handler():
    while True:
        choice = display_device_unitree_go_app_menu()
        if not handle_device_unitree_go_app_choice(choice):
            break