# Firmware Tools for Unitree Go2 Robots

This repository contains tools designed to configure and manipulate settings on Unitree Go2 Robots. These tools should be installed directly on the robot.

## Menu Overview

### Firmware Settings
1. **Spoof Model (AIR/PRO/EDU)** - Change the robot's model designation, particularly useful for accessing features exclusive to the EDU model.
2. **Spoof Region (US/CN/JP/DE/IN/FR/UK/BR/RU/CA/IT/ES/AU/MX/KR/ID/TR/SA/NL/CH)** - Modify the robot's region, initially aimed at switching from CN to other global regions.
3. **Spoof Serial Number** - Alter the robot's serial number; functionality is planned but not yet implemented.
4. **Change System Sounds** - Adjust the system sounds used by the robot

### DDS Settings
5. **Change DDS Domain ID** - Configure the DDS Domain ID to allow multiple robots to operate on the same network, ideal for collaborative robot scenarios.
6. **Change DDS Interface (eth0/wlan1)** - Toggle the network interface between wired (eth0) and wireless (wlan1) modes for flexibility in connectivity.

### Factory Settings
7. **Revert Single Service to Factory** - Restore a single selected service back to its original factory settings.
8. **Revert All Services to Factory** - Reset all services to their factory default settings for a comprehensive system restore.

### Network Settings
9. **Configure Interface Forwarding (eth0 <--> wlan1)** - Set up forwarding between ethernet and wireless interfaces to support reaching devices connected to eth0 through wlan1 (AP) (Under Development).

### System
10. **Reboot Device** - Perform a safe shutdown and reboot of the robot, ensuring no operational disruptions.
11. **Exit** - Exit the tool.

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
pip install -r requirements.txt
```

## Update

Should be in STA mode in order to have internet connection!
Connect via SSH to the dog and execute:
```bash
cd /unitree/dev/go2_firmware_tools
git fetch --all && git reset --hard origin/master
pip install -r requirements.txt
```

## Usage 
Launch the scipt and choose the required option:
```bash
cd /unitree/dev/go2_firmware_tools
python3 main.py
```

### Thanks

To TheRoboVerse community! Visit us at [TheRoboVerse](https://theroboverse.com) for more information and support.
