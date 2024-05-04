import sys
from device_managment import *

def patch_services():
    install_all_patches()

def change_model():
    model = input("Enter model (AIR/PRO/EDU): ")
    change_device_model(model)

def change_region():
    region = input("Enter region (RU/US/FR): ")
    print(f"Region changed to {region}")

def change_serial_number():
    serial_number = input("Enter new serial number: ")
    print(f"Serial number changed to {serial_number}")

def change_dds_domain_id():
    domain_id = input("Enter new DDS Domain ID: ")
    print(f"DDS Domain ID changed to {domain_id}")

def change_dds_interface():
    interface = input("Enter new interface (eth0/wlan1): ")
    print(f"DDS Interface changed to {interface}")

def install_update_sdk():
    print("Python SDK installed/updated")

def update_firmware_tools():
    print("Firmware tools updated")

def revert_services_to_factory():
    print("Revert Patches to Factory Selected")
    print("Patches reverted to factory settings")

def reboot_device():
    """Reboots the device by calling the operating system's reboot command."""
    try:
        logging.info("Attempting to reboot the device...")
        os.system('sudo reboot')
    except Exception as e:
        logging.error(f"An error occurred while trying to reboot the device: {e}")

def main():
    actions = {
        1: patch_services,
        2: change_model,
        3: change_region,
        4: change_serial_number,
        5: change_dds_domain_id,
        6: change_dds_interface,
        7: install_update_sdk,
        8: update_firmware_tools,
        9: revert_services_to_factory,
        10: reboot_device
    }

    while True:
        print("""
        1: Patch services     
        2: Change Model (AIR/PRO/EDU)
        3: Change Region (RU/US/FR)
        4: Change Serial Number
        5: Change DDS Domain ID
        6: Change DDS Interface (eth0/wlan1)
        7: Install/Update Python SDK
        8: Update Firmware Tools
        9: Revert Services to Factory
        10: Reboot device
        11: Exit
        """)
        try:
            choice = int(input("Select an option: "))
            if choice == 11:
                print("Exiting...")
                break
            action = actions.get(choice)
            if action:
                action()
            else:
                print("Invalid option, please try again.")
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    main()
