#!/bin/bash
sudo apt-get update
sudo apt-get install cmake build-essential

cd /unitree/dev/go2_firmware_tools
git fetch --all && git reset --hard origin/master
pip install -r requirements.txt
chmod +x update.sh
chmod +x start.sh