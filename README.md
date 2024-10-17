# Firmware Tools for Unitree Go2 Robots

This repository contains tools designed to configure and manipulate settings on Unitree Go2 Robots. These tools should be installed directly on the robot.

## Supported version
Currently supported firmware package 
- 1.0.24 
- 1.0.25 

## Menu Overview

### Device
1. **Show Device Info** - Show device info such as serial number, region, firmware, and hardware version
2. **Secondary development** - Enable/Disable secondary development. Useful for Air/Pro as this feature is turned off by default.
3. **Reboot** -  Reboot the device.
### Firmware
5. **Backup partitions** - Backup pre-uboot, uboot, boot, and uni partitions to the /unitree/tmp/backup folder.
6. **Flash partitions** - Flash partitions (not yet implemented).
7. **Install OTA updates** - Download and install official OTA update for PRO/EDU model. Usefull for AIR users to install full firmware package
### Network
8. **WiFi config** - Switch WiFi either to AP or STA mode.
9. **WebRTC config** - WebRTC config.
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
got checkout 1.0.24-1.0.25
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
