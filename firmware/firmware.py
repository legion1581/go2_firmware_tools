from . import firmware_backup
from . import firmware_ota
from InquirerPy import inquirer
from device.device_management import fetch_package_version

# 
# CMD MENU
#    

def display_firmware_menu():
    menu_items = [
        'Check Firmware Version',
        'Backup partitions',
        'Flash partitions',
        'Install OTA update',
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
        print(f"Package version: {fetch_package_version()}")
    elif choice == 'Backup partitions':
        firmware_backup.cli_handler()
    elif choice == 'Install OTA update':
        firmware_ota.cli_handler()
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