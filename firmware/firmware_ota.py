import random
import time
import threading
import subprocess
import requests
import json
import logging
from device import device_management
from tqdm import tqdm
from InquirerPy import inquirer
from .constants import ota_update_info
from util.utilities import create_directory

# Get the logger
logger = logging.getLogger('go2_firmware_tools')

def generate_random_token(length=32):
    """Generate a random hex token."""
    return ''.join(random.choices('0123456789abcdef', k=length))

def read_system_version():
    """
    Reads the "Version" value from a JSON file.

    :param file_path: The path to the JSON file.
    :return: The value of the "Version" field.
    """
    file_path = "/unitree/robot/pkg/package/package.json"
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data.get("Version")

def write_version_to_json(new_version):
    """
    Writes a new "Version" value to a JSON file.

    :param file_path: The path to the JSON file.
    :param new_version: The new version value to write.
    """
    file_path = "/unitree/robot/pkg/package/package.json"
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Update the "Version" field
    data["Version"] = new_version
    
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

    print(f"Updated 'Version' to {new_version} in {file_path}")

def download_file(url, local_filename):
    """
    Downloads a file from the given URL and saves it locally while displaying the download progress.

    :param url: The URL of the file to download.
    :param local_filename: The local file path where the downloaded file will be saved.
    """
    # Send a GET request to the URL with stream=True to download the file in chunks
    with requests.get(url, stream=True) as response:
        # Check if the request was successful
        response.raise_for_status()

        # Get the total file size from the response headers
        total_size = int(response.headers.get('content-length', 0))

        # Open a local file in write-binary mode
        with open(local_filename, 'wb') as file:
            # Initialize a progress bar using tqdm
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=local_filename, ascii=True) as pbar:
                # Iterate over the response content in chunks
                for chunk in response.iter_content(chunk_size=8192):
                    # Filter out keep-alive new chunks
                    if chunk:
                        # Write the chunk to the local file
                        file.write(chunk)
                        # Update the progress bar
                        pbar.update(len(chunk))

    print(f"Download complete: {local_filename}")

def tail_log_file(log_file_path, stop_event):
    """
    Continuously reads the log file and prints new lines as they appear,
    until the stop_event is set.

    :param log_file_path: The path to the log file to tail.
    :param stop_event: A threading.Event object used to signal when to stop tailing.
    """
    with open(log_file_path, 'r') as log_file:
        # Move to the end of the file
        log_file.seek(0, 2)

        while not stop_event.is_set():  # Keep running until the stop_event is set
            line = log_file.readline()
            if not line:
                time.sleep(0.1)  # Sleep briefly to avoid busy waiting
                continue
            print(line, end='')

def run_ota_update(version: str):
    """
    Runs the OTA update command.
    """
    if version not in ota_update_info:
        print(f"OTA version: {version} is not supported")
        return
    
    package_name, url, md5 = ota_update_info[version]

    command_path = '/unitree/ota/engine/bin/ota_utils'
    download_path = f"/unitree/ota/update/{version}"
    create_directory(download_path)
    download_file(url, f"{download_path}/{package_name}")

    # In case the update version matches the current, then downgrade it
    if read_system_version() == version:
        write_version_to_json("1.0.20")

    # Define the command to be executed
    command = [
        command_path,
        '-c', 'updatepackage',
        '-v', version,
        '-p', package_name,
        '-u', url,
        '-i', md5,
        '-t', generate_random_token(),
    ]

    # Create an Event object to signal the thread to stop
    stop_event = threading.Event()

    # Start tailing the log file in a separate thread
    log_file_path = '/unitree/var/log/ota_engine/ota_utils.LOG'
    log_thread = threading.Thread(target=tail_log_file, args=(log_file_path, stop_event))
    log_thread.start()

    # Execute the command without capturing output
    try:
        subprocess.run(command, check=True)
        print("OTA update completed...")
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)
    
    # Stop the log tailing thread after the OTA update is complete
    stop_event.set()
    log_thread.join()

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


# 
# CMD MENU
#    

def display_firmware_menu():
    menu_items = [
        'Update to 1.0.24 PRO/EDU',
        'Update to 1.0.25 PRO/EDU',
        'Update to 1.1.1 PRO/EDU',
        'Back to Main Menu',
        'Quit'
    ]
     
    choice = inquirer.select(
        message="Select an option:",
        choices=menu_items
    ).execute()

    return choice

def handle_firmware_choice(choice):
    if choice == 'Update to 1.0.24 PRO/EDU':
        run_ota_update("1.0.24")
        print(f"Updating to 1.0.24 PRO/EDU...")
    elif choice == 'Update to 1.0.25 PRO/EDU':
        run_ota_update("1.0.25")
        print(f"Updating to 1.0.25 PRO/EDU...")
    elif choice == 'Update to 1.1.1 PRO/EDU':
        run_ota_update("1.1.1")
        print(f"Updating to 1.1.1 PRO/EDU...")
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

   