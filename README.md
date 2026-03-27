# Firmware Tools for Unitree Go2 AIR/PRO/EDU

This repository contains tools designed to configure and manipulate settings on Unitree Go2 Robots. These tools should be installed directly on the robot.

## Supported version
Currently supported firmware package
- 1.1.1-1.1.14 (latest available)

For older firmware versions, use the appropriate branch:
* [1.0.24-1.0.25 branch](https://github.com/legion1581/go2_firmware_tools/tree/1.0.24-1.0.25)

## Menu Overview

### Device
1. **Show Device Info** - Show device info such as serial number, region, firmware, and hardware version
2. **Secondary development** - Checks the status of Secondary developemnt. This feature comes pre-enabled in custom firmware. For more details, refer to the "Install Custom Firmware" section in the menu.
3. **Unitree Go APP Compatibility** -  When enabled, this feature allows the use of the latest Unitree Go App with older versions of the Go2 firmware.
4. **Shut down all services** - Stops all services and powers down the robot, placing it in a safe state. This is ideal when performing system file manipulations or other maintenance tasks.
5. **Reboot** -  Reboot the device.
### Firmware
6. **Backup partitions** - Backup pre-uboot, uboot, boot, and uni partitions to the /unitree/tmp/backup folder.
7. **Install custom package** - Installs custom package with secondary development enabled, providing access to the full set of files from the PRO/EDU models. This is also perfect for AIR users who want to unlock the complete range of services, including AI mode.
8. **MCU** - Flasher for MCU. Required when updating from 1.0.x.x to 1.1.x
9. **Motors** - Flasher for Go2 motors. This Motor firmware was introduces in firmware version 1.0.24, presumably to support higher torques required for AI mode.
### Network
10. **WiFi config** - Switch WiFi either to AP or STA mode.
11. **WebRTC config** - WebRTC config.
    - **Multi-session**: Enable or disable multi-session support within WebRTC. This allows the device to handle multiple concurrent WebRTC sessions, which is useful for managing multiple remote connections simultaneously

## Installation

A custom firmware upgrade or jailbreak is required. For detailed instructions, visit [theroboverse.com](https://theroboverse.com).

After gaining root, follow these steps to install manually:

Connect via SSH to the dog and execute:
```bash
mkdir -p /unitree/dev
cd /unitree/dev
git clone https://github.com/legion1581/go2_firmware_tools.git
cd go2_firmware_tools
git checkout 1.1.x
chmod +x install.sh
./install.sh
```

## Update

Should be in STA mode in order to have internet connection!
Connect via SSH to the dog and execute:
```bash
./update.sh
```

## Usage
Launch the scipt and choose the required option:
```bash
cd /unitree/dev/go2_firmware_tools
./start.sh
```

### Thanks

To TheRoboVerse community! Visit us at [TheRoboVerse](https://theroboverse.com) for more information and support.

### Support

If you like this project, please consider buying me a coffee:

<a href="https://www.buymeacoffee.com/legion1581" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
