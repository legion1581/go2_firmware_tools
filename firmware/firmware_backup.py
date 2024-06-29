
import os
import subprocess
import json
import logging
import datetime
import hashlib
from InquirerPy import inquirer
from fdt import parse_dtb
from utilities import read_json_file, copy_file_with_progress, file_exists, rename_file, truncate_file, copy_file

# Get the logger
logger = logging.getLogger('go2_firmware_tools')

backup_folder = '/unitree/tmp/backup'

# 
# UBOOT BACKUP
# 
def _get_uboot_info(path):
    SZ = 0x200000
    with open(f'{path}', 'rb') as f:
        img = f.read()
    
    assert img[SZ:] == img[:SZ], "The uboot image does not contain the same data two times."

    dt = parse_dtb(img[:SZ])
    logger.debug(dt.to_dts())
    
    # Extract and convert the timestamp
    unix_timestamp = dt.get_property('timestamp')[0]
    if unix_timestamp is not None:
        # Convert the Unix timestamp to a datetime object
        dt_object = datetime.datetime.fromtimestamp(unix_timestamp)

        # Format the datetime object to DD_MM_YEAR_HOUR_MIN_SEC
        formatted_date = dt_object.strftime('%d_%m_%Y_%H_%M_%S')
        logger.info(f"Formatted timestamp: {formatted_date}")

    else:
        logger.error("Timestamp property not found in the device tree.")
        return None
    
    # Extract and convert the totalsize
    uboot_size = dt.get_property('totalsize')[0]
    if uboot_size is not None:
        logger.info(f"Uboot size: {uboot_size}")
    
    # Calculate the MD5 hash
    md5_hash = hashlib.md5(img[:uboot_size]).hexdigest()
    logger.info(f"MD5 hash: {md5_hash}")
    
    return formatted_date, uboot_size, md5_hash


def backup_uboot_from_partition():
    uboot_path = f'{backup_folder}/uboot.img'
    # Define the dd command
    dd_command = [
        'dd', 'if=/dev/mmcblk0p1', f'of={uboot_path}', 
        'bs=512'
    ]
    
    # Execute the dd command, redirecting stdout and stderr to /dev/null
    with open('/dev/null', 'w') as devnull:
        subprocess.run(dd_command, check=True, stdout=devnull, stderr=devnull)
    
    timestamp, uboot_size, md5 = _get_uboot_info(f'{uboot_path}')

    truncate_file(uboot_path, uboot_size)
    rename_file(uboot_path, f'{backup_folder}/uboot_{timestamp}_{md5}.img')

# 
# BOOT BACKUP
# 

def _get_boot_info(path):
    with open(f'{path}', 'rb') as f:
        img = f.read()

    dt = parse_dtb(img)
    logger.debug(dt.to_dts())
    
    # Extract and convert the timestamp
    unix_timestamp = dt.get_property('timestamp')[0]
    if unix_timestamp is not None:
        # Convert the Unix timestamp to a datetime object
        dt_object = datetime.datetime.fromtimestamp(unix_timestamp)

        # Format the datetime object to DD_MM_YEAR_HOUR_MIN_SEC
        formatted_date = dt_object.strftime('%d_%m_%Y_%H_%M_%S')
        logger.info(f"Formatted timestamp: {formatted_date}")

    else:
        logger.error("Timestamp property not found in the device tree.")
        return None
    
    # Extract and convert the totalsize
    boot_size = dt.get_property('totalsize')[0]
    if boot_size is not None:
        logger.info(f"boot size: {boot_size}")
    
    # Calculate the MD5 hash
    md5_hash = hashlib.md5(img[:boot_size]).hexdigest()
    logger.info(f"MD5 hash: {md5_hash}")
    
    return formatted_date, boot_size, md5_hash


def backup_boot_from_partition():
    boot_path = f'{backup_folder}/boot.img'
    # Define the dd command
    dd_command = [
        'dd', 'if=/dev/mmcblk0p4', f'of={boot_path}', 
        'bs=512'
    ]
    
    # Execute the dd command, redirecting stdout and stderr to /dev/null
    with open('/dev/null', 'w') as devnull:
        subprocess.run(dd_command, check=True, stdout=devnull, stderr=devnull)
    
    timestamp, boot_size, md5 = _get_boot_info(f'{boot_path}')

    truncate_file(boot_path, boot_size)
    rename_file(boot_path, f'{backup_folder}/boot_{timestamp}_{md5}.img')
    
# 
# USERDATA BACKUP
# 

def backup_data_from_userdata():
    # Define mount points and paths
    mount_point_1 = '/mnt/mmcblk0p8'
    mount_point_2 = '/mnt/linux-rootfs'
    rootfs_file = '/mnt/mmcblk0p8/linux-rootfs.img'
    boot_file = '/mnt/mmcblk0p8/boot.img'
    uboot_file = '/mnt/mmcblk0p8/loader2.img'
    version_file = '/mnt/linux-rootfs/unitree/robot/pkg/version/version.json'
    

    try:
        # Ensure mount points exist
        os.makedirs(mount_point_1, exist_ok=True)
        os.makedirs(mount_point_2, exist_ok=True)
        os.makedirs(backup_folder, exist_ok=True)

        # Mount the first partition
        subprocess.run(['sudo', 'mount', '/dev/mmcblk0p8', mount_point_1], check=True)

        if file_exists(rootfs_file):
            # Mount the image file
            subprocess.run(['sudo', 'mount', rootfs_file, mount_point_2], check=True)

            # Read the package version from the JSON file
            package_info = read_json_file(version_file)
            version = package_info.get('Package', 'Version not found') if package_info else 'Version not found'

            # Unmount linux-rootfs.img
            subprocess.run(['sudo', 'umount', mount_point_2], check=True)

            # Copy the image file to the backup folder
            copy_file_with_progress(rootfs_file, f"{backup_folder}/linux-rootfs-{version}.img")

        if file_exists(boot_file):
            backup_boot_path = f'{backup_folder}/boot_from_userdata.img'
            copy_file_with_progress(boot_file, f'{backup_boot_path}')

            timestamp, boot_size, md5 = _get_boot_info(f'{backup_boot_path}')
            truncate_file(f'{backup_boot_path}', boot_size)
            rename_file(backup_boot_path, f'{backup_folder}/boot_userdata_{timestamp}_{md5}.img')

        if file_exists(uboot_file):
            backup_uboot_path = f'{backup_folder}/uboot_from_userdata.img'
            copy_file_with_progress(uboot_file , f'{backup_uboot_path}')

            timestamp, uboot_size, md5 = _get_uboot_info(f'{backup_uboot_path}')
            truncate_file(f'{backup_uboot_path}', uboot_size)
            rename_file(backup_uboot_path, f'{backup_folder}/uboot_userdata_{timestamp}_{md5}.img')


        # Unmount the first partition
        subprocess.run(['sudo', 'umount', mount_point_1], check=True)


    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred: {e}")
        return 'An error occurred during mounting or unmounting.'
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 'Version file not found.'
    except json.JSONDecodeError as e:
        logger.error(f"Error reading JSON file: {e}")
        return 'Error reading version file.'

# 
# UNI BACKUP
# 

def backup_uni_from_partition():
    uni_path = f'{backup_folder}/uni.img'
    
    # Define the dd command
    dd_command = [
        'dd', 'if=/dev/mmcblk0p3', f'of={uni_path}', 
        'bs=512'
    ]
    
    # Execute the dd command, redirecting stdout and stderr to /dev/null
    with open('/dev/null', 'w') as devnull:
        subprocess.run(dd_command, check=True, stdout=devnull, stderr=devnull)
    
    # Read the content of the output file
    with open(uni_path, 'rb') as f:
        content = f.read()
        
    # Find the position of the last non-null byte
    last_non_null_byte = len(content) - 1
    while last_non_null_byte >= 0 and content[last_non_null_byte] == 0x00:
        last_non_null_byte -= 1

    # Truncate the file to remove trailing null bytes
    truncate_file(uni_path, last_non_null_byte + 1)
    
    # Read the device info file
    with open('/unitree/tmp/deviceInfo.txt', 'r') as file:
        data = file.read().strip()
    
    # Parse the output data
    sn = data[:16]
    region = data[16:18]
    hw = f"{data[18]}.{data[19]}"
    bluetooth = data[20:]

    # Rename the file with the extracted information
    new_file_name = f'uni_{sn}_{region}_{hw}_{bluetooth}.img'
    rename_file(uni_path, f'{backup_folder}/{new_file_name}')

    # duplicate the uni to userdata (recovery partition) to keep it more safe. 
    mount_point = '/mnt/mmcblk0p8'
    os.makedirs(mount_point, exist_ok=True)
    # Mount the userdata partition
    subprocess.run(['sudo', 'mount', '/dev/mmcblk0p8', mount_point], check=True)
    copy_file_with_progress(f'{backup_folder}/{new_file_name}', f'{mount_point}/{new_file_name}')
    # Unmount the userdata partition
    subprocess.run(['sudo', 'umount', mount_point], check=True)



# 
# CMD MENU
#    

def display_firmware_menu():
    menu_items = [
        'Backup uboot',
        'Backup boot',
        'Backup uni',
        'Backup userdata',
        'Backup ALL',
        'Back to Main Menu',
        'Quit'
    ]
     
    choice = inquirer.select(
        message="Select an option:",
        choices=menu_items
    ).execute()

    return choice

def handle_firmware_choice(choice):
    if choice == 'Backup uboot':
        backup_uboot_from_partition()
        print(f"Backup saved to {backup_folder}")
    elif choice == 'Backup boot':
        backup_boot_from_partition()
        print(f"Backup saved to {backup_folder}")
    elif choice == 'Backup uni':
        backup_uni_from_partition()
        print(f"Backup saved to {backup_folder}")
        print(f"Backup duplicated to recovery partition for safety")
    elif choice == 'Backup userdata':
        backup_data_from_userdata()
        print(f"Backup saved to {backup_folder}")
    elif choice == 'Backup ALL':
        backup_uboot_from_partition()
        backup_boot_from_partition()
        backup_uni_from_partition()
        backup_data_from_userdata()
        print(f"Backup saved to {backup_folder}")

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

   
# Example usage
if __name__ == "__main__":
    version = backup_uni_from_partition()