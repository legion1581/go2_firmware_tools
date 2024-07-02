interface_list = [
    'eth0',
    'wlan1'
]

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
        "/unitree/module/unitree_lidar/bin/unitree_lidar_dds_node": "service_hot_patch",
        "/unitree/module/unitree_lidar/bin/lidar_switch": "service_hot_patch",
        "/unitree/module/utrack/dds_parameter.json": "json_patch",
        "/unitree/module/video_hub/videohub": "service_hot_patch",
        "/unitree/module/voxel_height_mapping/config/config.yaml": "yaml_patch",
        "/unitree/module/vui_service/dds_parameter.json": "json_patch",
        "/unitree/module/webrtc_bridge/bin/unitreeWebRTCClientMaster": "service_hot_patch",
        "/unitree/module/webrtc_bridge/src/webrtc_dds_bridge/signal_server.py": "python_patch"
    },
    "1.0.24": {
        "/unitree/module/advanced_sport/dds_parameter.json": "json_patch",
        "/unitree/module/ai_sport/dds_parameter.json": "json_patch",
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
        "/unitree/module/unitree_lidar/bin/unitree_lidar_dds_node": "service_hot_patch",
        "/unitree/module/unitree_lidar/bin/lidar_switch": "service_hot_patch",
        "/unitree/module/unitree_lidar_slam/bin/dds_parameter.json": "json_patch",
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
        "unitreeWebRTCClientMaster": 0x20694,
        "unitree_lidar_dds_node": 0x122868,
        "lidar_switch": 0x183DC
    },
    "1.0.24": {
        "audiohub": 0x69ec,
        "videohub": 0x1fa4,
        "unitreeWebRTCClientMaster": 0x21f64,
        "unitree_lidar_dds_node": 0x122868,
        "lidar_switch": 0x183DC
    }
}
