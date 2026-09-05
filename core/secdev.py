"""
secdev.py — crypto-free "is secondary development enabled?" detection.

The old approach (compare each service binary's md5 to a per-firmware manifest)
breaks across firmware versions (different patched binaries each release). This
detector is **version-independent** and uses only observable behavior — never the
lowcmd/uni_sec crypto we reversed:

  1. edition  — ground truth from the /dev/uni_sec secure element (AIR/PRO/EDU).
  2. DDS      — /unitree/etc/cyclonedds.xml has a <Security> block? secured (stock
                Pro/Air) vs open (the master_service edition-decision was flipped).
  3. ver      — /unitree/robot/basic/ver last-2-digits edition vs the true SN
                edition; a divergence toward EDU is the ver-hack that opens things.
  4. lowcmd   — best-effort runtime probe: is rt/lowcmd plaintext or encrypted?
                classified by CDR-header + byte-entropy, NOT by decrypting it.

Verdict: on an AIR/PRO robot, open DDS (and/or EDU-effective ver, plaintext
lowcmd) == secondary development enabled; secured DDS == stock/disabled. A native
EDU robot is open by design.
"""
import os
import re
import shutil
import subprocess

EDITION = {1: "AIR", 2: "PRO", 4: "EDU", 3: "MAX"}
CYCLONEDDS_XML = "/unitree/etc/cyclonedds.xml"
VER_FILE = "/unitree/robot/basic/ver"


def dds_security(root=""):
    """'secured' if cyclonedds.xml carries a <Security> block, 'open' if not,
    None if the file is missing/unreadable."""
    path = root + CYCLONEDDS_XML
    try:
        with open(path, "r", errors="replace") as f:
            xml = f.read()
    except OSError:
        return None
    return "secured" if re.search(r"<\s*Security", xml, re.I) else "open"


def ver_edition(root=""):
    """Edition the firmware BELIEVES it is, from /unitree/robot/basic/ver
    (last 2 digits, e.g. ...02=PRO, ...04=EDU). None if absent."""
    try:
        with open(root + VER_FILE) as f:
            ver = f.read().strip()
    except OSError:
        return None
    if len(ver) >= 2 and ver[-2:].isdigit():
        return EDITION.get(int(ver[-2:]) % 10 if int(ver[-2:]) > 9 else int(ver[-2:]))
    if ver and ver[-1].isdigit():
        return EDITION.get(int(ver[-1]))
    return None


def _entropy(b):
    if not b:
        return 0.0
    from math import log2
    counts = [0] * 256
    for x in b:
        counts[x] += 1
    n = len(b)
    return -sum((c / n) * log2(c / n) for c in counts if c)


def classify_lowcmd(sample):
    """Plaintext vs encrypted from raw CDR bytes — no decryption.

    Plaintext unitree_hg LowCmd_ starts with the CDR header 00 01 00 00 and, at
    idle, is mostly zero (low entropy). Blowfish-ECB ciphertext is high-entropy
    with almost no zero bytes and no stable header.
    """
    if not sample or len(sample) < 16:
        return "not_seen"
    header_ok = sample[:4] in (b"\x00\x01\x00\x00", b"\x00\x03\x00\x00")
    zeros = sample.count(0) / len(sample)
    ent = _entropy(sample)
    if header_ok and (zeros > 0.15 or ent < 6.5):
        return "plaintext"
    if ent > 7.3 and zeros < 0.05:
        return "encrypted"
    return "plaintext" if header_ok else "encrypted"


def lowcmd_mode(root="", seconds=3):
    """Best-effort: sample rt/lowcmd via the robot's own cyclonedds CLI and
    classify. Returns plaintext/encrypted/not_seen/unavailable. Only meaningful
    on the robot itself (needs the DDS domain up)."""
    if root or not shutil.which("cyclonedds"):
        return "unavailable"
    env = dict(os.environ, CYCLONEDDS_URI=CYCLONEDDS_XML)
    # The CLI streams until interrupted; a timeout stops it and we read whatever
    # samples arrived. (Works whether or not the CLI supports an exit-after-N flag.)
    try:
        r = subprocess.run(["cyclonedds", "subscribe", "rt/lowcmd"],
                           env=env, capture_output=True, timeout=seconds)
        out = (r.stdout or b"") + (r.stderr or b"")
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"") + (e.stderr or b"")
    except OSError:
        return "unavailable"
    if not out.strip():
        return "not_seen"
    # If the CLI decoded a structured LowCmd, field names appear -> plaintext.
    if re.search(rb"mode_machine|motor_cmd|mode_pr|crc", out):
        return "plaintext"
    # Otherwise look at any hex payload it dumped and entropy-classify it.
    hexes = re.findall(rb"([0-9a-fA-F]{2}(?:[ :]?[0-9a-fA-F]{2}){15,})", out)
    if hexes:
        raw = bytes.fromhex(re.sub(rb"[^0-9a-fA-F]", b"", hexes[0]).decode())
        return classify_lowcmd(raw)
    return "not_seen"


def detect(robot, probe_lowcmd=True):
    """Comprehensive, crypto-free verdict. Returns a dict:
    {enabled: True/False/None, verdict: str, signals: {...}}."""
    root = robot.root
    info = robot.info()
    sn_ed = info.edition
    dds = dds_security(root)
    ver_ed = ver_edition(root)
    lc = lowcmd_mode(root) if probe_lowcmd else "unavailable"
    sig = {"edition_true": sn_ed, "dds": dds, "ver_edition": ver_ed, "lowcmd": lc}

    def out(enabled, verdict):
        return {"enabled": enabled, "verdict": verdict, "signals": sig}

    if sn_ed == "EDU":
        return out(True, "EDU — open by design (secondary dev is native)")
    # AIR / PRO (or unknown edition): stock is secured + encrypted.
    if dds == "secured":
        return out(False, "disabled — secured DDS (stock)")
    if dds == "open":
        v = f"ENABLED — open DDS on a {sn_ed or '?'} robot"
        if lc == "plaintext":
            v += "; rt/lowcmd plaintext ✓"
        elif lc == "encrypted":
            v += "; ⚠ rt/lowcmd still encrypted (basic_service not patched?)"
        return out(True, v)
    # DDS xml unreadable — fall back to ver / lowcmd.
    if ver_ed == "EDU" and sn_ed in ("PRO", "AIR"):
        return out(True, f"ENABLED — ver hacked to EDU on a {sn_ed} robot")
    if lc == "plaintext":
        return out(True, "ENABLED — rt/lowcmd plaintext")
    if lc == "encrypted":
        return out(False, "disabled — rt/lowcmd encrypted")
    return out(None, "unknown — could not read cyclonedds.xml / ver / lowcmd")
