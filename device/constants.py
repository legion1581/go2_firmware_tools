
basic_dir_path = '/unitree/robot/basic'  # Absolute path might be needed depending on the system setup
tmp_dir_path = '/unitree/tmp'

model_id_to_name = {
    1: "AIR",
    2: "PRO",
    4: "EDU"
}

# Reverse the dictionary to map from names to IDs
model_name_to_id = {name: id for id, name in model_id_to_name.items()}

services_path = {
    "basic_service_check": "/unitree/robot/tool/basic_service_check",
    "vui_service": "/unitree/module/vui_service/vui_service"
}

service_list = [
    "sport_mode",
    "advanced_sport",
    "ai_sport",
    "motion_switcher",
    "basic_service",
    "audio_hub",
    "bashrunner",
    "chat_go",
    "robot_state",
    "obstacles_avoid",
    "utrack",
    "unitree_lidar",
    "unitree_lidar_slam",
    "video_hub",
    "voxel_height_mapping",
    "vui_service",
    "webrtc_bridge",
    "webrtc_multicast_responder",
    "webrtc_signal_server",
    "net_switcher",
    "master_service",
]


services_sha = {
    "1.0.25": {
        "factory": {
            "basic_service_check": "2a2d6897d239baa4f5fb5b7b87dc1fd35bd83bb802c52ee6e57f1bbb54693d1c",
            "vui_service": "4434d7ff14ba749b969833d1374ca5e727de1b5a725f58766d3c6000b0fddf22"
        },
        "patched": {
            "basic_service_check": "8698762221907f676ab1dbdc7232ea040155a4fb55a1412e50de15dbf4d0a88d",
            "vui_service": "175b1f4a04fb697e443da8a3e2561a6d799899e7d1c57284519ea734e225696b"
        }
    }
}

