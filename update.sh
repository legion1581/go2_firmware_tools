#!/bin/bash
cd /unitree/dev/go2_firmware_tools
git fetch --all && git reset --hard origin/1.1.1
pip install -r requirements.txt
chmod +x update.sh
chmod +x start.sh