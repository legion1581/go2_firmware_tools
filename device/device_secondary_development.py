import logging
from InquirerPy import inquirer
from . import device_management, device_services

# Get the logger
logger = logging.getLogger('go2_firmware_tools')

def secondary_development_status():
    real_model = device_management.get_real_model()

    if real_model == "EDU":
        print("Secondary development is switched on by default on EDU model")
        return True
    
    spoofed_model = device_management.get_spoofed_model()
    # print(f"Real model: {real_model}, spoofed model: {spoofed_model}")
    is_patched = device_services.is_patch_installed("basic_service_check") and\
        device_services.is_patch_installed("basic_service") and\
        device_services.is_patch_installed("master_service") 

    status = (real_model != spoofed_model) and is_patched
    print("Secondary development status: " + ("ENABLED" if status else "DISABLED"))
    return status

def secondary_development_enable():
    if secondary_development_status():
        return

    real_model = device_management.get_real_model()

    device_services.stop_all_services()
    device_services.install_service_patch("basic_service_check")
    device_services.install_service_patch("basic_service")
    device_services.install_service_patch("master_service")

    if real_model == "AIR":
        prompt = "AIR vui_service patch required. Install it now? ([yes]/no): "
        while True:
            user_input = input(prompt).strip().lower()
            if user_input in ["yes", ""]:
                # device_services.install_service_patch("vui_service", stop_service_flag=True)
                print("!!!Not yet supported!!!")
                break
            elif user_input == "no":
                logger.info("Operation canceled by user.")
                return False
            else:
                logger.info("Invalid input. Please answer 'yes' or press Enter to continue, 'no' to cancel.")

    prompt = "Reboot required, reboot now? ([yes]/no): "
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ["yes", ""]:
            device_management.reboot_device()
            break
        elif user_input == "no":
            break
        else:
            logger.info("Invalid input. Please answer 'yes' or press Enter to continue, 'no' to cancel.")

    return True

def secondary_development_disable():
    if not secondary_development_status():
        return

    real_model = device_management.get_real_model()

    device_services.stop_all_services()
    device_services.install_factory_service("basic_service_check")
    device_services.install_factory_service("basic_service")
    device_services.install_factory_service("master_service")

    if real_model == "AIR" and device_services.is_patch_installed("vui_service"):
        # device_services.install_service_patch("vui_service", stop_service_flag=True)
        print("!!!Not yet supported!!!")

    prompt = "Reboot required, reboot now? ([yes]/no): "
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ["yes", ""]:
            device_management.reboot_device()
            break
        elif user_input == "no":
            break
        else:
            logger.info("Invalid input. Please answer 'yes' or press Enter to continue, 'no' to cancel.")

    return True


# 
# CMD MENU
#    

def display_device_secondary_dev_menu():
    menu_items = [
        'Status',
        'Enable',
        'Disable',
        'Back to Main Menu',
        'Quit'
    ]
     
    choice = inquirer.select(
        message="Select an option:",
        choices=menu_items
    ).execute()

    return choice

def handle_device_secondary_dev_choice(choice):
    if choice == 'Status':
        secondary_development_status()
    elif choice == 'Enable':
        secondary_development_enable()
    elif choice == 'Disable':
        secondary_development_disable()
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