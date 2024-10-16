from . import wifi_config, webrtc_managment
from InquirerPy import inquirer

# 
# CMD MENU
#    

def display_network_menu():
    menu_items = [
        'WiFi config',
        'WebRTC config',
        'Back to Main Menu',
        'Quit'
    ]
     
    choice = inquirer.select(
        message="Select an option:",
        choices=menu_items
    ).execute()

    return choice

def handle_network_choice(choice):
    if choice == 'WiFi config':
        wifi_config.cli_handler()
    elif choice == 'WebRTC config':
        webrtc_managment.cli_handler()
    elif choice == 'Back to Main Menu':
        return False
    elif choice == 'Quit':
        exit()
    else:
        print("Invalid choice, please try again.")
    return True

def cli_handler():
    while True:
        choice = display_network_menu()
        if not handle_network_choice(choice):
            break