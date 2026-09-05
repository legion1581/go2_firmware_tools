"""Platform detection: pick the right Robot for the box we're running on."""
import os

from .base import Robot, RobotInfo, parse_identity
from .r1 import R1Robot
from .g1 import G1Robot
from .go2 import Go2Robot

_BY_NAME = {"R1": R1Robot, "G1": G1Robot, "GO2": Go2Robot, "GO2AIR": Go2Robot}


def detect(root="", force=None):
    """Return a Robot instance. `force` (or $UNITREE_PLATFORM) overrides auto-detect."""
    force = force or os.environ.get("UNITREE_PLATFORM")
    if force:
        cls = _BY_NAME.get(force.upper().replace("_", "").replace(" ", ""))
        if not cls:
            raise ValueError(f"unknown platform override: {force}")
        return cls(root=root)

    # secure-element robots (R1 / G1) expose /dev/uni_sec; Go2 uses the flash partition.
    if os.path.exists(root + "/dev/uni_sec"):
        return _hint_humanoid(root)
    if os.path.exists(root + "/dev/mmcblk0p3"):
        return Go2Robot(root=root)
    # last resort: assume R1 (the primary target) so the menu still loads
    return R1Robot(root=root)


def _hint_humanoid(root):
    """R1 vs G1 both have uni_sec — disambiguate from the firmware package string."""
    try:
        import json
        with open(root + "/unitree/robot/pkg/version/version.json") as f:
            pkg = (json.load(f).get("Package") or "").upper()
        if "G1" in pkg:
            return G1Robot(root=root)
    except Exception:
        pass
    return R1Robot(root=root)
