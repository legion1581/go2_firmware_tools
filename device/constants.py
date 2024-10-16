
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
    "vui_service": "/unitree/module/vui_service/vui_service",
    "basic_service": "/unitree/module/basic_service/basic_service",
    "master_service": "/unitree/module/master_service/master_service"

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
    "1.1.1": {
        "factory": {
            "basic_service_check": "2b3c5ec92c1ff1e8587108a09edae5871275d51b3b5997aa2716bc65a5960719",
            "basic_service": "ee143dcc7256e392cf3ec05c5269a6ccd8fa35af33c30363aced8b0368699285",
            "master_service": "dfb88239a3abd84e762fcb29ea10216c4aff462040825d350ed8dc8320526dc3",
            "vui_service" : "66f756d386be94a273dc731f711327e1d021c5c2a31a912cdccb41458a087d4c"
        },
        "patched": {
            "basic_service_check": "b5a96c1828ae2816d27d7877a956d047df804c4b8ee9f97e54c5c83add769a3b",
            "basic_service": "c20bbbd8082319cb55d847a2002c471ecce595a1acf3983740d12e2211448737",
            "master_service": "20bf108dd58a7bed3e1e39080e6f1f134768e443083321c545e0d9e85a25990d",
            "vui_service" : "935386b86a630059cdff461d0b2aba9f46e49d522d4b0347cf72cc5f5595d6a3"
        }
    }
}

