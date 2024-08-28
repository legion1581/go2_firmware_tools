import json
from InquirerPy import inquirer
from device.device_services import restart_service

def read_webrtc_config():
    """
    Reads the WebRTC bridge configuration from a JSON file.

    :return: The configuration as a Python dictionary.
    """
    file_path = "/unitree/etc/master_service/service/webrtc_bridge"
    with open(file_path, 'r') as file:
        return json.load(file)

def write_webrtc_config(data):
    """
    Writes the WebRTC bridge configuration to a JSON file.

    :param data: The configuration data as a Python dictionary.
    """
    file_path = "/unitree/etc/master_service/service/webrtc_bridge"
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def multi_session_status():
    """
    Checks and prints the status of the '--enable_multi_session true' parameter in the 'Start' command.
    """
    config = read_webrtc_config()
    start_cmd = config.get("Start", {}).get("Cmd", "")
    status = "--enable_multi_session true" in start_cmd
    print("Multi-session status: " + ("ENABLED" if status else "DISABLED"))
    return status  # Return status to be used in other functions

def multi_session_enable():
    """
    Enables the '--enable_multi_session true' parameter in the 'Start' command if not already enabled.
    """
    config = read_webrtc_config()
    if not multi_session_status():
        if "--enable_multi_session true" not in config["Start"]["Cmd"]:
            config["Start"]["Cmd"] += " --enable_multi_session true"
        write_webrtc_config(config)  # Save the updated configuration
        restart_service("webrtc_bridge")  # Restart the service to apply changes
        print("WebRTC multi-session enabled.")
    else:
        print("WebRTC multi-session is already enabled.")

def multi_session_disable():
    """
    Disables the '--enable_multi_session true' parameter in the 'Start' command if currently enabled.
    """
    config = read_webrtc_config()
    if multi_session_status():
        config["Start"]["Cmd"] = config["Start"]["Cmd"].replace(" --enable_multi_session true", "")
        write_webrtc_config(config)  # Save the updated configuration
        restart_service("webrtc_bridge")  # Restart the service to apply changes
        print("WebRTC multi-session disabled.")
    else:
        print("WebRTC multi-session is already disabled.")

# 
# CMD MENU
#

def display_device_secondary_dev_menu():
    """
    Displays the secondary device menu and gets user input.

    :return: The user's choice.
    """
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
    """
    Handles the user's choice from the secondary device menu.

    :param choice: The user's choice.
    :return: True if the menu should continue displaying, False otherwise.
    """
    if choice == 'Status':
        multi_session_status()
    elif choice == 'Enable':
        multi_session_enable()
    elif choice == 'Disable':
        multi_session_disable()
    elif choice == 'Back to Main Menu':
        return False
    elif choice == 'Quit':
        exit()
    else:
        print(f"Invalid choice, please try again. choice: {choice}")
    return True

def cli_handler():
    """
    Continuously displays the secondary device menu and handles user input until the user chooses to exit.
    """
    while True:
        choice = display_device_secondary_dev_menu()
        if not handle_device_secondary_dev_choice(choice):
            break

if __name__ == "__main__":
    cli_handler()
