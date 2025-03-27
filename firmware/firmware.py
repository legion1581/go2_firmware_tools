from . import firmware_backup, firmware_custom_package, firmware_mcu
from InquirerPy import inquirer
from device.device_management import fetch_package_version, fetch_custom_package_version

def display_firmware_version():
    # Fetch custom package version and determine the final package version string
    custom_package_version = fetch_custom_package_version()
    if custom_package_version:  # Check if custom_package_version is not None or empty
        package_version = f"{fetch_package_version()} mod {custom_package_version}"
    else:
        package_version = fetch_package_version()

    print(f"Package ver: {package_version}")

# 
# CMD MENU
#    

def display_firmware_menu():
    menu_items = [
        'Check Firmware Version',
        'Backup partitions',
        'Install custom package',
        'MCU',
        'Motors',
        'Back to Main Menu',
        'Quit'
    ]
     
    choice = inquirer.select(
        message="Select an option:",
        choices=menu_items
    ).execute()

    return choice

def handle_firmware_choice(choice):
    if choice == 'Update Firmware':
        pass
    elif choice == 'Check Firmware Version':
        display_firmware_version()
    elif choice == 'Backup partitions':
        firmware_backup.cli_handler()
    elif choice == 'Install custom package':
        firmware_custom_package.cli_handler()
    elif choice == 'MCU':
        firmware_mcu.cli_handler()
    elif choice == 'Back to Main Menu':
        return False
    elif choice == 'Quit':
        exit()
    else:
        print("Invalid choice, please try again.")
    return True

def cli_handler():
    while True:
        choice = display_firmware_menu()
        if not handle_firmware_choice(choice):
            break