"""
supervisor.py — install/remove the unitree-guardian lock-out failsafe.

Guardian = a systemd service that keeps sshd alive and restores last-known-good
WiFi if the stack fails to come up. On R1/G1 this is the prerequisite for enabling
secondary development (so a bad patch can never lock you out).
"""
import os
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(REPO, "assets", "supervisor")

SCRIPT_SRC = os.path.join(ASSETS, "unitree-guardian.sh")
UNIT_SRC = os.path.join(ASSETS, "unitree-guardian.service")
SCRIPT_DST = "/usr/local/sbin/unitree-guardian.sh"
UNIT_DST = "/etc/systemd/system/unitree-guardian.service"


def _run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def is_installed():
    return os.path.isfile(SCRIPT_DST) and os.path.isfile(UNIT_DST)


def status():
    if not is_installed():
        return {"installed": False, "enabled": False, "active": False}
    en = _run("systemctl is-enabled unitree-guardian 2>/dev/null").stdout.strip()
    ac = _run("systemctl is-active unitree-guardian 2>/dev/null").stdout.strip()
    return {"installed": True, "enabled": en == "enabled", "active": ac == "active",
            "enabled_raw": en, "active_raw": ac}


def install(log=print):
    import shutil
    if not os.path.isfile(SCRIPT_SRC) or not os.path.isfile(UNIT_SRC):
        raise FileNotFoundError("guardian assets missing from the tool")
    os.makedirs(os.path.dirname(SCRIPT_DST), exist_ok=True)
    shutil.copyfile(SCRIPT_SRC, SCRIPT_DST); os.chmod(SCRIPT_DST, 0o755)
    shutil.copyfile(UNIT_SRC, UNIT_DST); os.chmod(UNIT_DST, 0o644)
    log("  ✓ installed guardian script + unit")
    for cmd in ("systemctl daemon-reload",
                "systemctl enable unitree-guardian",
                "systemctl start unitree-guardian"):
        r = _run(cmd)
        if r.returncode != 0 and r.stderr.strip():
            log(f"  ! {cmd}: {r.stderr.strip()}")
    st = status()
    log(f"  guardian: enabled={st['enabled']} active={st['active']}")
    return st


def uninstall(log=print):
    for cmd in ("systemctl disable --now unitree-guardian",):
        _run(cmd)
    for p in (UNIT_DST, SCRIPT_DST):
        try:
            os.remove(p)
        except FileNotFoundError:
            pass
    _run("systemctl daemon-reload")
    log("  ✓ guardian removed")
    return True
