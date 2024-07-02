
basic_dir_path = '/unitree/robot/basic'  # Absolute path might be needed depending on the system setup

model_id_to_name = {
    1: "AIR",
    2: "PRO",
    4: "EDU"
}

# Reverse the dictionary to map from names to IDs
model_name_to_id = {name: id for id, name in model_id_to_name.items()}

services_path = {
    "basic_service_check": "/unitree/robot/tool/basic_service_check",
    "master_service": "/unitree/module/master_service/master_service",
    "vui_service": "/unitree/module/vui_service/vui_service"
}

service_list = [
    "sport_mode",
    "advanced_sport",
    "motion_switcher",
    "basic_service",
    "audio_hub",
    "bashrunner",
    "chat_go",
    "robot_state",
    "obstacles_avoid",
    "utrack",
    "unitree_lidar",
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
            "vui_service": "1dd64bce98015b33ad3d58487276f6c1f90900d7632bf8e9fe519ab555f5c45a"
        },
        "patched": {
            "basic_service_check": "8698762221907f676ab1dbdc7232ea040155a4fb55a1412e50de15dbf4d0a88d",
            "vui_service": "f2bfc57d90dd691624de386be3ebb7200dec31048a770dd9b71efa2cb2a7a17e"
        }
    }
}

