# Firmware Tools for Unitree Go2 Robots

This repository contains tools designed to configure and manipulate settings on Unitree Go2 Robots. These tools should be installed directly on the robot.

## Supported Commands
1. Spoof Model (AIR/PRO/EDU)
2. Spoof Region (US/CN/JP/DE/IN/FR/UK/BR/RU/CA/IT/ES/AU/MX/KR/ID/TR/SA/NL/CH)
3. Spoof Serial Number (Not yet implemented)
4. Change DDS Domain ID (Not yet implemented)
5. Change DDS Interface (eth0/wlan1)
6. Revert Single Service to Factory Settings
7. Revert All Services to Factory Settings
8. Reboot Device
9. Exit

### Spoof Model
Allows users to change the robot's model designation. This is particularly useful for AIR/PRO users who wish to access features exclusive to the EDU model.

### Spoof Region
Changes the robot's region setting. Initially designed to switch from CN to global regions. This feature has not been tested for compatibility with the global Unitree Go2 app.

### Spoof Serial Number
Functionality to spoof the serial number is planned but not yet implemented.

### Change DDS Domain ID
Intended to allow multiple robots to operate on the same network by assigning unique DDS Domain IDs (range from 0 to 255). This feature is under development.

### Change DDS Interface (eth0/wlan1)
Switches the network interface between wired (eth0) and wireless (wlan1) modes, enabling use of official SDK tools and other DDS instances over WiFi.

### Revert Single Service to Factory Settings
Restores individual services to their original factory state.

### Revert All Services to Factory Settings
Resets all services to their default factory settings.

### Reboot Device
Safely powers down the robot and reboots the system.

## Installation

### Option 1: Pre-installed Package
The tools may already be included in custom firmware versions:
For more details, please visit [theroboverse.com](https://theroboverse.com) and join our Discord community.

### Option 2: Manual Installation
A custom firmware upgrade is required. For detailed instructions, visit [theroboverse.com](https://theroboverse.com). Follow these steps to install manually:

```bash
ssh root@[ip_address_of_the_robot]
mkdir -p /unitree/dev
cd /unitree/dev
git clone https://github.com/legion1581/go2_firmware_tools.git
cd go2_firmware_tools
python3 main.py
```

### Thanks

To TheRoboVerse community! Visit us at [TheRoboVerse](https://theroboverse.com) for more information and support.
