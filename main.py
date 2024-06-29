import logging
from InquirerPy import inquirer
from firmware import firmware
import device_managment

# Configure basic logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Get the logger
logger = logging.getLogger('go2_firmware_tools')
logger.setLevel(logging.WARNING)

# Ensure that the root logger has the correct level
logging.getLogger().setLevel(logging.WARNING)

def main_menu():
    menu_items = [
        'Device',
        'Firmware',
        'Networking',
        'DDS',
        'Quit'
    ]
    
    choice = inquirer.select(
        message="Select an option:",
        choices=menu_items
    ).execute()

    return choice

if __name__ == '__main__':
    device_managment.fetch_device_data()
    while True:
        choice = main_menu()
        if choice == 'Firmware':
            firmware.cli_handler()
        elif choice == 'Device':
            device_managment.cli_handler()
        # elif choice == 'DDS':
        #     dds.cli_handler()
        elif choice == 'Quit':
            break
