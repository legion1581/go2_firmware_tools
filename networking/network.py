from . import wifi_config
from InquirerPy import inquirer

# 
# CMD MENU
#    

def display_network_menu():
    menu_items = [
        'WiFi config',
        'DDS config',
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
        pass
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