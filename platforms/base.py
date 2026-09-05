"""
base.py — the universal robot model.

Identity is one 29-byte ASCII "Hardware" block, identical across R1/G1/Go2:
    [0:16]  serial number      (edition is derived from sn[4])
    [16:18] country/region
    [18:20] hardware rev        ("10" -> "1.0")
    [20:25] bluetooth code
    [25:29] reserved
Only the *source* of that block differs per platform (uni_sec ioctl vs flash
partition), so each Robot subclass just implements read_identity_block().
"""
import json
import os
from dataclasses import dataclass, field

EDITION = {1: "AIR", 2: "PRO", 4: "EDU", 3: "MAX"}


def rkss_secure_boot(root="", device=None):
    """READ-ONLY RK secure-boot check. A signed Rockchip loader carries the
    'RKSS' magic at sector 64 (offset 0x8000) of the boot block device; an
    unsigned/insecure loader does not. Returns True/False, or None if the device
    can't be read (unknown — never assume 'disabled'). Never writes.

    Mirrors the Go2 tool's `dd if=/dev/mmcblk0 bs=512 skip=64 count=1` check, but
    as a plain 4-byte seek+read (no dd, no temp file, no write to the partition).
    """
    cands = [device] if device else []
    cands += [root + "/dev/mmcblk0", "/dev/mmcblk0"]  # R1/Go2 eMMC
    for d in cands:
        if not d:
            continue
        try:
            with open(d, "rb") as f:          # opened O_RDONLY
                f.seek(64 * 512)
                return f.read(4) == b"RKSS"
        except (FileNotFoundError, PermissionError, IsADirectoryError, OSError):
            continue
    return None


@dataclass
class RobotInfo:
    platform: str = "?"
    sn: str = ""
    edition: str = "?"
    region: str = ""
    hardware: str = ""
    bluetooth: str = ""
    firmware: str = ""
    firmware_mod: str = ""
    secure_boot: bool = None      # True / False / None = unknown (couldn't read)
    identity_source: str = ""
    extra: dict = field(default_factory=dict)


def parse_identity(block):
    """Parse a >=25-byte ASCII identity block into fields."""
    b = block.decode("ascii", "replace") if isinstance(block, (bytes, bytearray)) else block
    sn = b[0:16].strip("\x00 ")
    edition = "?"
    if len(sn) >= 5 and sn[4].isdigit():
        edition = EDITION.get(int(sn[4]), "?")
    hw_raw = b[18:20].strip("\x00 ")
    hardware = f"{hw_raw[0]}.{hw_raw[1]}" if len(hw_raw) == 2 else hw_raw
    return {
        "sn": sn,
        "edition": edition,
        "region": b[16:18].strip("\x00 "),
        "hardware": hardware,
        "bluetooth": b[20:25].strip("\x00 "),
    }


class Robot:
    platform = "?"
    services_path = {}                       # name -> on-robot destination path
    version_json = "/unitree/robot/pkg/version/version.json"

    def __init__(self, root=""):
        self.root = root.rstrip("/")

    # --- to be provided per platform ---
    def read_identity_block(self):
        """Return the >=25-byte ASCII identity block (raise on failure)."""
        raise NotImplementedError

    def read_secure_boot(self):
        return None

    # --- shared ---
    def firmware_version(self):
        try:
            with open(self.root + self.version_json) as f:
                j = json.load(f)
            return j.get("Package", ""), j.get("Mod", "")
        except Exception:
            return "", ""

    def info(self):
        i = RobotInfo(platform=self.platform)
        try:
            block = self.read_identity_block()   # may update self.identity_source
            fields = parse_identity(block)
            i.sn = fields["sn"]; i.edition = fields["edition"]; i.region = fields["region"]
            i.hardware = fields["hardware"]; i.bluetooth = fields["bluetooth"]
        except Exception as e:
            i.extra["identity_error"] = str(e)
        i.identity_source = self.identity_source
        i.firmware, i.firmware_mod = self.firmware_version()
        try:
            i.secure_boot = self.read_secure_boot()
        except Exception:
            pass
        return i

    identity_source = "?"
