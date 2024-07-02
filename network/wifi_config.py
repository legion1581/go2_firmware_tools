import os
import stat
import subprocess
import logging
from InquirerPy import inquirer

# Get the logger
logger = logging.getLogger('go2_firmware_tools')

# 
# WiFi Config AP
# 

def _switch_to_AP(ssid, passphrase):
    script_path = '/unitree/module/network_manager/upper_bluetooth/hostapd_restart.sh'

    # Get the current permissions
    current_permissions = os.stat(script_path).st_mode

    # Add execute permission for the user, group, and others
    os.chmod(script_path, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    ap_restart_command = [
        f'{script_path}', f'{ssid}', f'{passphrase}'
    ]
    try:
        subprocess.run(ap_restart_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart hostapd with SSID '{ssid}' and passphrase '{passphrase}'.")
        print(f"Command returned non-zero exit status {e.returncode}.")

def cli_switch_to_AP():
    ssid = input("Enter AP SSID: ")
    passphrase = input("Enter AP passphrase: ")
    _switch_to_AP(ssid, passphrase)

# 
# WiFi Config STA
# 

def _switch_to_STA(ssid, passphrase):
    script_path = '/unitree/module/network_manager/upper_bluetooth/wpa_supplicant_restart.sh'

    # Get the current permissions
    current_permissions = os.stat(script_path).st_mode

    # Add execute permission for the user, group, and others
    os.chmod(script_path, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    sta_restart_command = [
        f'{script_path}', f'{ssid}', f'{passphrase}'
    ]
    try:
        subprocess.run(sta_restart_command, check=True)
    except subprocess.CalledProcessError as code:
        return_code = code.returncode
        if return_code == 130:
            print(f"Successfully connected to target WiFi station '{ssid}' and can ping through the target address.")
        elif return_code == 131:
            print(f"Connected to target WiFi station '{ssid}' but cannot ping through the target address.")
        elif return_code == 129:
            print(f"Failed to connect to target WiFi station '{ssid}'.")
        else:
            print(f"Command failed with return code {return_code}.")

def cli_switch_to_STA():
    ssid = input("Enter STA SSID: ")
    passphrase = input("Enter STA passphrase: ")
    _switch_to_STA(ssid, passphrase)

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
        cli_switch_to_STA()
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