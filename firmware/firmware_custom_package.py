import os
import json
import shutil
import logging
import subprocess
from InquirerPy import inquirer
from util.yandexDownloader import YandexDiskDownloader
from util.utilities import run_shell_command
from .constants import custom_package_description_file_js
from device.device_services import stop_all_services
from device import device_management, device_services


# Get the logger
logger = logging.getLogger('go2_firmware_tools')

# Optional cleanup manifest extracted from the custom package. Lists absolute
# paths that should be removed after the new package is laid down on disk,
# so files dropped between firmware versions don't linger.
REMOVE_LIST_PATH = "/unitree/tmp/custom_package_remove_list.txt"


def apply_remove_list(remove_list_path: str = REMOVE_LIST_PATH):
    """
    Deletes paths listed in the remove_list manifest, then deletes the
    manifest itself. The manifest is optional: missing file or missing
    entries are silently ignored. Blank lines and lines starting with '#'
    are skipped.
    """
    if not os.path.isfile(remove_list_path):
        return

    try:
        with open(remove_list_path, "r") as f:
            entries = f.readlines()
    except OSError:
        return

    removed = 0
    for raw in entries:
        path = raw.strip()
        if not path or path.startswith("#"):
            continue
        try:
            if os.path.islink(path) or os.path.isfile(path):
                os.remove(path)
                removed += 1
            elif os.path.isdir(path):
                shutil.rmtree(path)
                removed += 1
        except OSError:
            pass

    try:
        os.remove(remove_list_path)
    except OSError:
        pass

    if removed:
        print(f"Cleaned up {removed} stale path(s) from previous package.")


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

def download_latest_custom_package_info(download_location: str = "./downloads"):
    # Create the download directory if it doesn't exist
    os.makedirs(download_location, exist_ok=True)

    print(f"Downloading custom package info...")

    # Initialize the downloader and start the download
    downloader = YandexDiskDownloader(custom_package_description_file_js, download_location)
    file_name = downloader.download()

    return file_name


def download_custom_package_from_yandex_disk(package_link: str, md5sum: str, download_location: str = "./downloads"):
    """
    Downloads a custom package file from Yandex Disk using the provided package link.

    Args:
        package_link (str): The direct download link for the package package on Yandex Disk.
        download_location (str): The directory where the package should be saved. Defaults to "./downloads".

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


def run_package_flasher(version: str):
    """
    Runs the custom package installation.
    """
    download_dir = "./downloads"

    try:
        # Step 1: Download the custom package info
        custom_package_info_file_name = download_latest_custom_package_info()
        custom_package_info_file_path = os.path.join(download_dir, custom_package_info_file_name)

        # Step 2: Load the JSON file
        with open(custom_package_info_file_path, "r") as file:
            custom_info_js_data = json.load(file)

        # Step 3: Get the link to the appropriate package version
        real_model = device_management.get_real_model()

        if real_model in ['AIR', 'PRO', 'EDU', 'MAX']:
            package_link = custom_info_js_data.get('custom_package_info', {}).get(version, {}).get("AIR_PRO_EDU")
            md5sum = custom_info_js_data.get('custom_package_info', {}).get(version, {}).get("md5")
        else:
            raise ValueError(f"Unsupported device model: {real_model}")

        # Step 4: Download the custom package
        print(f"Downloading package version {version}...")
        custom_package_file_name = download_custom_package_from_yandex_disk(package_link, md5sum)
        package_path = os.path.join(download_dir, custom_package_file_name)

        # Step 5: Stop all services
        stop_all_services()

        # Step 6: Extract the package
        print(f"Extracting package from '{package_path}'...")
        extract_tar_xz(package_path, extract_dir="/")

        # Step 6b: Apply optional cleanup manifest bundled in the package.
        apply_remove_list()

        # Step 7: Run post-install scripts
        print(f"Running post-install commands...")
        run_shell_command("/unitree/opt/lib/vlc/vlc-cache-gen /unitree/opt/lib/vlc/plugins")
        run_shell_command("ldconfig")
        run_shell_command("if [ ! -e /usr/lib/aarch64-linux-gnu/libgomp-d22c30c5.so.1.0.0 ]; then ln -s /usr/lib/aarch64-linux-gnu/libgomp.so.1.0.0 /usr/lib/aarch64-linux-gnu/libgomp-d22c30c5.so.1.0.0; fi")
        
        # STEP 8: for AIR model, patch the VUI service
        # Skip patch installation for 1.1.7 (Not ready yet)
        if real_model == 'AIR' and version != '1.1.7':
            device_services.install_service_patch("vui_service", stop_service_flag=True)

        # Installation Complete
        print("Package installation complete.")

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
        raise RuntimeError(f"An error occurred during package installation: {e}")


# 
# CMD MENU
#    

def display_custom_package_menu():
    menu_items = [
        'Install custom package 1.1.1',
        'Install custom package 1.1.2',
        'Install custom package 1.1.3',
        'Install custom package 1.1.4',
        'Install custom package 1.1.7',
        'Install custom package 1.1.11',
        'Install custom package 1.1.15',
        'Back to Main Menu',
        'Quit'
    ]
     
    choice = inquirer.select(
        message="Select an option:",
        choices=menu_items
    ).execute()

    return choice

def handle_custom_package_choice(choice):
    if choice == 'Install custom package 1.1.1':
        run_package_flasher("1.1.1")
    elif choice == 'Install custom package 1.1.2':
        run_package_flasher("1.1.2")
    elif choice == 'Install custom package 1.1.3':
        run_package_flasher("1.1.3")
    elif choice == 'Install custom package 1.1.4':
        run_package_flasher("1.1.4")
    elif choice == 'Install custom package 1.1.7':
        run_package_flasher("1.1.7")
    elif choice == 'Install custom package 1.1.11':
        run_package_flasher("1.1.11")
    elif choice == 'Install custom package 1.1.15':
        run_package_flasher("1.1.15")
    elif choice == 'Back to Main Menu':
        return False
    elif choice == 'Quit':
        exit()
    else:
        print(f"Invalid choice, please try again. choice : {choice}")
    return True

def cli_handler():
    while True:
        choice = display_custom_package_menu()
        if not handle_custom_package_choice(choice):
            break

# Example usage
if __name__ == "__main__":
    run_package_flasher("1.1.1")