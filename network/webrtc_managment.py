from InquirerPy import inquirer
from . import webrtc_multi_session

# 
# CMD MENU
#    

def display_device_menu():
    menu_items = [
        'Multi session',
        'Back to Main Menu',
        'Quit'
    ]
     
    choice = inquirer.select(
        message="Select an option:",
        choices=menu_items
    ).execute()

    return choice

def handle_device_choice(choice):
    if choice == 'Multi session':
        webrtc_multi_session.cli_handler()
    elif choice == 'Back to Main Menu':
        return False
    elif choice == 'Quit':
        exit()
    else:
        print(f"Invalid choice, please try again. choice : {choice}")
    return True

def cli_handler():
    while True:
        choice = display_device_menu()
        if not handle_device_choice(choice):
            break