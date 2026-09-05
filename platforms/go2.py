"""Go2: identity read as ASCII directly from the uni flash partition."""
import os

from .base import Robot

UNI_PART = "/dev/mmcblk0p3"
ID_OFF = 2304        # 0x900
ID_LEN = 25
PRELOADER = "/dev/mmcblk0"


class Go2Robot(Robot):
    platform = "Go2"
    services_path = {
        "master_service": "/unitree/module/master_service/master_service",
        "basic_service": "/unitree/module/basic_service/basic_service",
        "basic_service_check": "/unitree/robot/tool/basic_service_check",
        "vui_service": "/unitree/module/vui_service/vui_service",
    }
    identity_source = "uni partition"

    def read_identity_block(self):
        path = self.root + UNI_PART
        with open(path, "rb") as f:
            f.seek(ID_OFF)
            block = f.read(ID_LEN)
        if len(block) < ID_LEN:
            raise RuntimeError(f"short read from {path}")
        return block

    def read_secure_boot(self):
        try:
            with open(self.root + PRELOADER, "rb") as f:
                f.seek(64 * 512)
                return f.read(4) == b"RKSS"
        except Exception:
            return False
