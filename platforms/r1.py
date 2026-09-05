"""R1 humanoid: identity from the /dev/uni_sec secure element."""
import fcntl
import os

from .base import Robot

# /dev/uni_sec ioctls (fixed 1024-byte secure blob; _IOC size field ignored)
IOCTL_SECURE_RSA_R = 0x80045202  # read blob
UNISEC_DEV = "/dev/uni_sec"
UNISEC_BLOB_LEN = 1024
HW_OFF = 0x100   # 29-byte ASCII Hardware block lives here in the blob
HW_LEN = 29

# fallback: the same fields, written out as plain files by the self-check
BASIC_DIR = "/unitree/robot/basic"


def read_uni_sec_blob(dev=UNISEC_DEV):
    buf = bytearray(UNISEC_BLOB_LEN)
    fd = os.open(dev, os.O_RDWR)
    try:
        fcntl.ioctl(fd, IOCTL_SECURE_RSA_R, buf, True)
    finally:
        os.close(fd)
    return bytes(buf)


class R1Robot(Robot):
    platform = "R1"
    services_path = {
        "master_service": "/unitree/module/master_service/master_service",
        "basic_service": "/unitree/module/basic_service/basic_service",
        "basic_service_check": "/unitree/robot/tool/basic_service_check",
        "net-init": "/unitree/etc/master_service/cmd/net-init",
    }
    identity_source = "uni_sec"

    def read_identity_block(self):
        dev = self.root + UNISEC_DEV
        if os.path.exists(dev):
            try:
                blob = read_uni_sec_blob(dev)
                self.identity_source = "uni_sec"
                return blob[HW_OFF:HW_OFF + HW_LEN]
            except Exception as e:
                self._unisec_err = str(e)
        # fallback: assemble from /unitree/robot/basic/{code,country,Hardware,bluetooth}
        block = self._from_basic_files()
        if block is not None:
            self.identity_source = "basic/ files"
            return block
        raise RuntimeError(
            f"cannot read identity: {UNISEC_DEV} unavailable"
            + (f" ({getattr(self, '_unisec_err', '')})" if hasattr(self, "_unisec_err") else "")
            + f" and {BASIC_DIR} files missing")

    def _from_basic_files(self):
        d = self.root + BASIC_DIR
        try:
            def rd(n):
                with open(os.path.join(d, n)) as f:
                    return f.read().strip()
            sn = rd("code"); country = rd("country"); hw = rd("Hardware"); bt = rd("bluetooth")
        except Exception:
            return None
        s = f"{sn:<16}{country:<2}{hw:<2}{bt:<5}"
        return s.encode("ascii", "replace")

    def read_secure_boot(self):
        # Real check: RK signed-loader 'RKSS' magic at sector 64 of the eMMC
        # (read-only 4-byte read; never writes). None if the device isn't readable.
        from .base import rkss_secure_boot
        return rkss_secure_boot(self.root)
