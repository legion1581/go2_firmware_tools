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
### Network
7. **WiFi config** - Switch WiFi either to AP or STA mode.
8. **DDS config** -DDS config (not yet implemented).

 
## Dependences

Install the folowing packages
```bash
sudo apt-get update
sudo apt-get install cmake build-essential
```

## Installation

### Option 1: Pre-installed Package
The tools may already be included in custom firmware versions:
For more details, please visit [theroboverse.com](https://theroboverse.com) and join our Discord community.

### Option 2: Manual Installation
A custom firmware upgrade is required. For detailed instructions, visit [theroboverse.com](https://theroboverse.com). Follow these steps to install manually:


Connect via SSH to the dog and execute:
```bash
mkdir -p /unitree/dev
cd /unitree/dev
git clone https://github.com/legion1581/go2_firmware_tools.git
cd go2_firmware_tools
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
