"""G1 humanoid: same uni_sec secure element as R1 (paths TBD, fill when targeted)."""
from .r1 import R1Robot


class G1Robot(R1Robot):
    platform = "G1"
    # G1 shares the /dev/uni_sec identity mechanism with R1. Service destinations
    # are the same module layout on current firmware; override here if they diverge.
    services_path = {
        "master_service": "/unitree/module/master_service/master_service",
        "basic_service": "/unitree/module/basic_service/basic_service",
        "basic_service_check": "/unitree/robot/tool/basic_service_check",
        "net-init": "/unitree/etc/master_service/cmd/net-init",
    }
