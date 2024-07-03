from InquirerPy import inquirer
from . import device_management, device_secondary_development

# 
# CMD MENU
#    

def display_device_menu():
    menu_items = [
        'Show Device Info',
        'Secondary Development',
        'Reboot',
        'Back to Main Menu',
        'Quit'
    ]
     
    choice = inquirer.select(
        message="Select an option:",
        choices=menu_items
    ).execute()

    return choice

def handle_device_choice(choice):
    if choice == 'Show Device Info':
        device_management.print_device_data()
    elif choice == 'Secondary Development':
        device_secondary_development.cli_handler()
    elif choice == 'Reboot':
        device_management.reboot_device()
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