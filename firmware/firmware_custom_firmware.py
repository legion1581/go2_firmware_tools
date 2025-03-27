import os
import json
import logging
import subprocess
from InquirerPy import inquirer
from util.yandexDownloader import YandexDiskDownloader
from util.utilities import run_shell_command
from .constants import custom_firmware_description_file_js
from device.device_services import stop_all_services
from device import device_management, device_services


# Get the logger
logger = logging.getLogger('go2_firmware_tools')


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

def download_latest_custom_firmware_info(download_location: str = "./downloads"):
    # Create the download directory if it doesn't exist
    os.makedirs(download_location, exist_ok=True)

    print(f"Downloading custom firmware info...")

    # Initialize the downloader and start the download
    downloader = YandexDiskDownloader(custom_firmware_description_file_js, download_location)
    file_name = downloader.download()

    return file_name


def download_custom_package_from_yandex_disk(package_link: str, md5sum: str, download_location: str = "./downloads"):
    """
    Downloads a custom package file from Yandex Disk using the provided package link.

    Args:
        package_link (str): The direct download link for the firmware package on Yandex Disk.
        download_location (str): The directory where the firmware should be saved. Defaults to "./downloads".

    Returns:
        str: The name of the downloaded package file.

    Raises:
        ValueError: If the download fails or the package link is invalid.
    """

    # Create the download directory if it doesn't exist
    os.makedirs(download_location, exist_ok=True)

    # Initialize the downloader and start the download
    downloader = YandexDiskDownloader(package_link, download_location, md5sum)
    file_name = downloader.download()

    print("Download complete.")

    return file_name



def extract_tar_xz(file_path: str, extract_dir: str = "/"):
    """
    Extracts a .tar.xz archive using the system `tar` command.

    Args:
        file_path (str): The path to the .tar.xz file.
        extract_dir (str): The directory where the archive should be extracted.
                           Defaults to the root directory ("/").

    Raises:
        FileNotFoundError: If the .tar.xz file does not exist.
        RuntimeError: If the `tar` command fails.
    """
    # Validate the input file path
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    # Ensure the extraction directory exists
    os.makedirs(extract_dir, exist_ok=True)

    print(f"Extracting '{file_path}' to '{extract_dir}'...")

    try:
        # Build the tar command
        command = [
            "tar",
            "-xJpf",  # Options: extract (x), xz compression (J), preserve permissions (p), file input (f)
            file_path,
            "-C",     # Specify the extraction directory
            extract_dir
        ]

        # Run the tar command
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Print success message
        print("Extraction complete.")
    except subprocess.CalledProcessError as e:
        # Handle errors from the tar command
        error_message = e.stderr.decode().strip() if e.stderr else "Unknown error"
        raise RuntimeError(f"Failed to extract archive: {error_message}")
    except FileNotFoundError:
        # Handle the case where the `tar` command is not found
        raise RuntimeError("`tar` command not found. Ensure it is installed and available in your PATH.")


def run_firmware_flasher(version: str):
    """
    Runs the custom firmware installation.
    """
    download_dir = "./downloads"

    try:
        # Step 1: Download the custom firmware info
        custom_firmware_info_file_name = download_latest_custom_firmware_info()
        custom_firmware_info_file_path = os.path.join(download_dir, custom_firmware_info_file_name)

        # Step 2: Load the JSON file
        with open(custom_firmware_info_file_path, "r") as file:
            custom_info_js_data = json.load(file)

        # Step 3: Get the link to the appropriate package version
        real_model = device_management.get_real_model()

        if real_model in ['AIR', 'PRO', 'EDU', 'MAX']:
            package_link = custom_info_js_data.get('custom_firmware_info', {}).get(version, {}).get("AIR_PRO_EDU")
            md5sum = custom_info_js_data.get('custom_firmware_info', {}).get(version, {}).get("md5")
        else:
            raise ValueError(f"Unsupported device model: {real_model}")

        # Step 4: Download the custom package
        print(f"Downloading package version {version}...")
        custom_firmware_file_name = download_custom_package_from_yandex_disk(package_link, md5sum)
        firmware_path = os.path.join(download_dir, custom_firmware_file_name)

        # Step 5: Stop all services
        stop_all_services()

        # Step 6: Extract the firmware
        print(f"Extracting package from '{firmware_path}'...")
        extract_tar_xz(firmware_path, extract_dir="/")


        # Step 7: Run post-install scripts
        print(f"Running post-install commands...")
        run_shell_command("/unitree/opt/lib/vlc/vlc-cache-gen /unitree/opt/lib/vlc/plugins")
        run_shell_command("ldconfig")
        run_shell_command("if [ ! -e /usr/lib/aarch64-linux-gnu/libgomp-d22c30c5.so.1.0.0 ]; then ln -s /usr/lib/aarch64-linux-gnu/libgomp.so.1.0.0 /usr/lib/aarch64-linux-gnu/libgomp-d22c30c5.so.1.0.0; fi")
        
        # STEP 8: for AIR model, patch the VUI service
        if real_model == 'AIR':
            device_services.install_service_patch("vui_service", stop_service_flag=True)

        # Installation Complete
        print("Firmware installation complete.")

        # Step 9: Prompt for reboot
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
    except Exception as e:
        raise RuntimeError(f"An error occurred during firmware installation: {e}")


# 
# CMD MENU
#    

def display_custom_firmware_menu():
    menu_items = [
        'Install custom firmware 1.1.1',
        'Install custom firmware 1.1.2',
        'Install custom firmware 1.1.3',
        'Install custom firmware 1.1.4',
        'Back to Main Menu',
        'Quit'
    ]
     
    choice = inquirer.select(
        message="Select an option:",
        choices=menu_items
    ).execute()

    return choice

def handle_custom_firmware_choice(choice):
    if choice == 'Install custom firmware 1.1.1':
        run_firmware_flasher("1.1.1")
    elif choice == 'Install custom firmware 1.1.2':
        run_firmware_flasher("1.1.2")
    elif choice == 'Install custom firmware 1.1.3':
        run_firmware_flasher("1.1.3")
    elif choice == 'Install custom firmware 1.1.4':
        run_firmware_flasher("1.1.4")
    elif choice == 'Back to Main Menu':
        return False
    elif choice == 'Quit':
        exit()
    else:
        print(f"Invalid choice, please try again. choice : {choice}")
    return True

def cli_handler():
    while True:
        choice = display_custom_firmware_menu()
        if not handle_custom_firmware_choice(choice):
            break

# Example usage
if __name__ == "__main__":
    run_firmware_flasher("1.1.1")