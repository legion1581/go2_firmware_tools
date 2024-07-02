from InquirerPy import inquirer
from . import device_managment

def secondary_development_status():
    pass

# 
# CMD MENU
#    

def display_device_secondary_dev_menu():
    menu_items = [
        'Status',
        'Enable',
        'Disable',
        'Quit'
    ]
     
    choice = inquirer.select(
        message="Select an option:",
        choices=menu_items
    ).execute()

    return choice

def handle_device_secondary_dev_choice(choice):
    if choice == 'Status':
        pass
    elif choice == 'Back to Main Menu':
        return False
    elif choice == 'Quit':
        exit()
    else:
        print(f"Invalid choice, please try again. choice : {choice}")
    return True

def cli_handler():
    while True:
        choice = display_device_secondary_dev_menu()
        if not handle_device_secondary_dev_choice(choice):
            break