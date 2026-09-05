"""Small filesystem/hash helpers shared by the installer and platforms."""
import hashlib
import os
import shutil


def md5(path, _bufsize=1 << 16):
    """MD5 hex digest of a file, or None if it does not exist."""
    if not os.path.isfile(path):
        return None
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(_bufsize), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def file_mode(path):
    """Permission bits (e.g. 0o755) of an existing file, or None."""
    try:
        return os.stat(path).st_mode & 0o777
    except OSError:
        return None


def copy_preserving_mode(src, dst, mode=None):
    """Copy src->dst atomically-ish (write temp in dst dir, then rename).

    mode: an int (0o755) to force, or None to keep dst's existing mode when it
    exists, else fall back to the src mode.
    """
    ensure_dir(os.path.dirname(dst))
    keep = file_mode(dst) if mode is None else mode
    tmp = dst + ".fwtools.tmp"
    shutil.copyfile(src, tmp)
    if keep is None:
        keep = file_mode(src) or 0o644
    os.chmod(tmp, keep)
    os.replace(tmp, dst)  # atomic on same filesystem
    return keep


def parse_mode(mode):
    """Accept '0755', '0o755', 493, etc. -> int."""
    if isinstance(mode, int):
        return mode
    s = str(mode).strip()
    if s.startswith("0o"):
        return int(s, 8)
    if s.startswith("0") and len(s) > 1:
        return int(s, 8)
    return int(s, 8)  # bare octal like '755'


def human_size(n):
    size = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{int(size)} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{n} B"
