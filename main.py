import os
import logging
from InquirerPy import inquirer
from firmware import firmware
from network import network
from device import device

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
        'Network',
        'Quit'
    ]
    
    choice = inquirer.select(
        message="Select an option:",
        choices=menu_items
    ).execute()

    return choice

if __name__ == '__main__':
    main_py_dir = os.path.dirname(os.path.abspath(__file__))
    device.device_management.device_init(main_py_dir)

    while True:
        choice = main_menu()
        if choice == 'Firmware':
            firmware.cli_handler()
        elif choice == 'Device':
            device.cli_handler()
        elif choice == 'Network':
            network.cli_handler()
        # elif choice == 'DDS':
        #     dds.cli_handler()
        elif choice == 'Quit':
            break
