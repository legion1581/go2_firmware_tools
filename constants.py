
basic_dir_path = '/unitree/robot/basic'  # Absolute path might be needed depending on the system setup
tmp_dir_path = '/unitree/tmp'


model_id_to_name = {
    1: "AIR",
    2: "PRO",
    4: "EDU"
}

common_regions = [
    "US",  # United States
    "CN",  # China
    "JP",  # Japan
    "DE",  # Germany
    "IN",  # India
    "FR",  # France
    "UK",  # United Kingdom
    "BR",  # Brazil
    "RU",  # Russia
    "CA",  # Canada
    "IT",  # Italy
    "ES",  # Spain
    "AU",  # Australia
    "MX",  # Mexico
    "KR",  # South Korea
    "ID",  # Indonesia
    "TR",  # Turkey
    "SA",  # Saudi Arabia
    "NL",  # Netherlands
    "CH"   # Switzerland
]

interface_list = [
    'eth0',
    'wlan1'
]

# Reverse the dictionary to map from names to IDs
model_name_to_id = {name: id for id, name in model_id_to_name.items()}

services_path = {
    "basic_service_check": "/unitree/robot/tool/basic_service_check",
    "master_service": "/unitree/module/master_service/master_service",
    "vui_service": "/unitree/module/vui_service/vui_service",
    "audiohub": "/unitree/module/audio_hub/audiohub",
    "videohub": "/unitree/module/video_hub/videohub",
    "unitreeWebRTCClientMaster": "/unitree/module/webrtc_bridge/bin/unitreeWebRTCClientMaster"
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
    "1.0.23": {
        "factory": {
            "basic_service_check": "2a2d6897d239baa4f5fb5b7b87dc1fd35bd83bb802c52ee6e57f1bbb54693d1c",
            "master_service": "1bc07a31eb0ec27100fa7c51cc6f699d52b224e45b37bfba02d6d92645342958",
            "vui_service": "7469ec3d70c350f699225d3e7b75294e08b8c2ce9d3e9e758bc08f16ca82949b"
        },
        "patched": {
            "basic_service_check": "b9c4caf3f15948773009aa3891b97c8489b21df88458cdc846d6f37f1fa4fd9c",
            "master_service": "06f79ddf80b5fcaaa1e0d571cc9e1fcadc735f22569fda9e25075648e393b7ec",
            "vui_service": "035538130eb77ea22b0939b441abff4f4b1038d2861a6163ea5cb25d4a0043d4"
        }
    }
}

dds_domain_patch_list = {
    "1.0.23": {
        "/unitree/module/advanced_sport/dds_parameter.json": "json_patch",
        "/unitree/module/audio_hub/audiohub": "service_hot_patch",
        "/unitree/module/audio_hub/audio_player/util.py": "python_patch",
        "/unitree/module/bashrunner/bashrunner.py": "python_patch",
        "/unitree/module/basic_service/basic_service.json": "json_patch",
        "/unitree/module/chat_go/util.py": "python_patch",
        "/unitree/module/motion_switcher/motion_switcher_service.json": "json_patch",
        "/unitree/module/net_switcher/net_switcher.py": "python_patch",
        "/unitree/module/obstacles_avoid/dds_parameter.json": "json_patch",
        "/unitree/module/robot_state/robot_state_service.json": "json_patch",
        "/unitree/module/robot_state/config_service.json": "json_patch",
        "/unitree/module/sbus_handle/dds_parameter.json": "json_patch",
        "/unitree/module/sport_mode/dds_parameter.json": "json_patch",
        "/unitree/module/unitree_lidar/config/config.yaml": "yaml_patch",
        "/unitree/module/utrack/dds_parameter.json": "json_patch",
        "/unitree/module/video_hub/videohub": "service_hot_patch",
        "/unitree/module/voxel_height_mapping/config/config.yaml": "yaml_patch",
        "/unitree/module/vui_service/dds_parameter.json": "json_patch",
        "/unitree/module/webrtc_bridge/bin/unitreeWebRTCClientMaster": "service_hot_patch",
        "/unitree/module/webrtc_bridge/src/webrtc_dds_bridge/signal_server.py": "python_patch"
    }
}

dds_domain_service_patch_offset = {
    "1.0.23": {
        "audiohub": 0x69ec,
        "videohub": 0x1fa4,
        "unitreeWebRTCClientMaster": 0x20694
    }
}