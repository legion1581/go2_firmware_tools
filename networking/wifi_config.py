import os
import subprocess
import logging
from InquirerPy import inquirer

# Get the logger
logger = logging.getLogger('go2_firmware_tools')

# 
# WiFi Config
# 

def _switch_to_AP(ssid, passphrase):
    network_manager_path = '/unitree/module/network_manager/upper_bluetooth'
    ap_restart_command = [
        f'{network_manager_path}/hostapd_restart.sh', f'{ssid}', f'{passphrase}'
    ]
    subprocess.run(ap_restart_command, check=True)

def cli_switch_to_AP():
    ssid = input("Enter AP SSID: ")
    passphrase = input("Enter AP passphrase: ")
    _switch_to_AP(ssid, passphrase)

# 
# CMD MENU
#    

def display_firmware_menu():
    menu_items = [
        'Switch to STA mode',
        'Switch to AP mode',
        'Back to Main Menu',
        'Quit'
    ]
     
    choice = inquirer.select(
        message="Select an option:",
        choices=menu_items
    ).execute()

    return choice

def handle_firmware_choice(choice):
    if choice == 'Switch to STA mode':
        pass
    elif choice == 'Switch to AP mode':
        cli_switch_to_AP()
    elif choice == 'Back to Main Menu':
        return False
    elif choice == 'Quit':
        exit()
    else:
        print(f"Invalid choice, please try again. choice : {choice}")
    return True

def cli_handler():
    while True:
        choice = display_firmware_menu()
        if not handle_firmware_choice(choice):
            break