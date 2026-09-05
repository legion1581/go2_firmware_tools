"""
secondary_dev.py — enable / disable / status of secondary development.

Enable flow (R1/G1):
  1. require the guardian failsafe (auto-offer install) so a bad patch can't lock you out,
  2. resolve the package (Yandex download+verify, or a local dir/zip),
  3. preflight + confirm,
  4. stop the running stack the OTA way (mscli stopservice … + master), behind a
     motion-safety confirm, so no live service clobbers a patched file,
  5. md5-gated backup+replace+verify (core.installer),
  6. power-cycle (turn OFF then ON) to load the new binaries.
Disable = stop the stack + restore the newest backup (or factory) + power-cycle.
"""
import glob
import os
import tempfile

import config
from core import installer, secdev, service_control, yandex
from . import supervisor


def stop_stack_guarded(robot, assume_yes=False, confirm=input, log=print):
    """Stop the running stack the OTA way (full stop incl. master) before we
    replace any binary, with a motion-safety gate. Returns True if stopped.

    Patched files only take effect on reboot, but a live service can rewrite the
    file we just patched — so we stop first, exactly like Install.CmdPreList.
    """
    if robot.platform not in ("R1", "G1"):
        return service_control.stop_stack(robot.platform, include_master=True, log=log)
    log("\n⚠  R1/G1 is a STANDING humanoid. Stopping the motion stack will drop it.")
    log("   Lay the robot down / secure it on a stand BEFORE continuing.")
    if not assume_yes:
        ans = confirm("   Type STOP to stop the stack (anything else cancels): ").strip()
        if ans != "STOP":
            log("   Stack stop cancelled — nothing changed.")
            return False
    return service_control.stop_stack(robot.platform, include_master=True, log=log)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_DIR = os.path.join(REPO, "assets", "manifests")


def local_manifest(platform, firmware):
    """Load the manifest bundled in the tool (offline status/preflight)."""
    # exact match first, then any manifest for the platform
    exact = os.path.join(MANIFEST_DIR, f"{platform}_{firmware}.json")
    path = exact if os.path.isfile(exact) else None
    if not path:
        cand = sorted(glob.glob(os.path.join(MANIFEST_DIR, f"{platform}_*.json")))
        path = cand[-1] if cand else None
    if not path:
        return None
    return installer.load_manifest(path)


def status(robot, probe_lowcmd=True):
    """Version-independent verdict via observable behavior (edition + open DDS +
    plaintext lowcmd), plus an optional per-file md5 detail if a manifest is
    bundled. Returns (verdict_dict, files_report_or_None).

    verdict_dict = {enabled: True/False/None, verdict: str, signals: {...}}.
    Pass probe_lowcmd=False to skip the ~3s live rt/lowcmd DDS probe (info card).
    """
    verdict = secdev.detect(robot, probe_lowcmd=probe_lowcmd)
    files = None
    m = local_manifest(robot.platform, robot.firmware_version()[0])
    if m:
        try:
            files = installer.Installer(root=robot.root).status(m)[1]
        except Exception:
            files = None
    return verdict, files


def resolve_package(robot, local=None, log=print):
    """Return (pkg_dir, manifest, cleanup_dir_or_None). Downloads if needed."""
    fw = robot.firmware_version()[0]
    cleanup = None
    if local:
        if os.path.isdir(local):
            pkg_dir = local
        elif local.endswith(".zip"):
            pkg_dir = tempfile.mkdtemp(prefix="fwtools_pkg_"); cleanup = pkg_dir
            yandex.extract_zip(local, pkg_dir)
        else:
            raise ValueError("--package must be a directory or a .zip")
    else:
        pk = config.package_for(robot.platform, fw)
        if not pk or not pk.get("zip_link"):
            raise ValueError(
                f"no download link configured for {robot.platform} {fw}. "
                "Upload the package to Yandex and set config.PACKAGES, or pass a local "
                "package with --package <dir|zip>.")
        os.makedirs(config.DOWNLOAD_DIR, exist_ok=True)
        log("Downloading package…")
        zpath = yandex.download(pk["zip_link"], config.DOWNLOAD_DIR, expect_md5=pk.get("zip_md5"))
        pkg_dir = tempfile.mkdtemp(prefix="fwtools_pkg_"); cleanup = pkg_dir
        yandex.extract_zip(zpath, pkg_dir)
    manifest = installer.load_manifest(os.path.join(pkg_dir, "manifest.json"))
    return pkg_dir, manifest, cleanup


def enable(robot, local=None, assume_yes=False, confirm=input, log=print):
    """Enable secondary development. Returns True if a reboot is warranted."""
    # 1) guardian gate (hard prerequisite on humanoids)
    if robot.platform in ("R1", "G1"):
        st = supervisor.status()
        if not st["installed"]:
            log("\nThe SSH/WiFi guardian failsafe is REQUIRED before patching R1/G1 "
                "(a bad patch can otherwise lock you out).")
            ans = "y" if assume_yes else confirm("Install the guardian now? [Y/n]: ").strip().lower()
            if ans in ("", "y", "yes"):
                supervisor.install(log=log)
                if not supervisor.status()["installed"]:
                    log("Guardian install failed — aborting."); return False
            else:
                log("Aborting: guardian is required."); return False

    pkg_dir, manifest, cleanup = resolve_package(robot, local=local, log=log)
    try:
        inst = installer.Installer(root=robot.root)
        pf = inst.preflight(pkg_dir, manifest)
        log("\nPlan:")
        for r in pf:
            log(f"  {r['name']:20s} {r['verdict']}")
        if all(r["verdict"] == installer.INSTALLED for r in pf):
            log("\nAlready fully enabled. Nothing to do."); return False
        if not assume_yes:
            ans = confirm("\nProceed with backup + install? [y/N]: ").strip().lower()
            if ans not in ("y", "yes"):
                log("Cancelled."); return False
        # stop the running stack (OTA way) so no live service clobbers the patch
        stop_stack_guarded(robot, assume_yes=assume_yes, confirm=confirm, log=log)
        log("")
        backup_dir, _ = inst.install(pkg_dir, manifest, log=log)
        if backup_dir:
            log(f"\nOriginals backed up to: {backup_dir}")
        log("Secondary development installed. Power-cycle the robot (turn OFF, then ON) to activate.")
        return True
    finally:
        if cleanup:
            import shutil; shutil.rmtree(cleanup, ignore_errors=True)


def list_backups(robot):
    """Newest-first list of restore points (for the picker)."""
    return installer.Installer(root=robot.root).list_backups()


def restore_backup(robot, backup=None, assume_yes=False, confirm=input, log=print):
    """Restore the ORIGINALS saved before patching. `backup` = a dict from
    list_backups() (default: newest). Fully offline. Returns reboot-warranted."""
    inst = installer.Installer(root=robot.root)
    if backup is None:
        backups = inst.list_backups()
        if not backups:
            log("No backups found. Use 'Restore factory' to install the vanilla files "
                "from the package instead."); return False
        backup = backups[0]
    log(f"Restoring backup {backup['ts']} (the files saved before patching):")
    if not assume_yes and confirm("Proceed? [y/N]: ").strip().lower() not in ("y", "yes"):
        log("Cancelled."); return False
    stop_stack_guarded(robot, assume_yes=assume_yes, confirm=confirm, log=log)
    inst.restore_backup(backup, log=log)
    log("Restored. Power-cycle the robot (turn OFF, then ON) to activate.")
    return True


def restore_factory(robot, local=None, assume_yes=False, confirm=input, log=print):
    """Install the vanilla files shipped in the package's factory/ tree, IGNORING any
    local backups (needs a download or --package). Returns reboot-warranted."""
    try:
        pkg_dir, manifest, cleanup = resolve_package(robot, local=local, log=log)
    except Exception as e:
        log(f"Cannot factory-restore: {e}"); return False
    try:
        if not manifest.get("has_factory"):
            log("This package carries no factory/ originals."); return False
        log("Factory restore installs the ORIGINAL vanilla files from the package, "
            "ignoring any local backups.")
        if not assume_yes and confirm("Proceed? [y/N]: ").strip().lower() not in ("y", "yes"):
            log("Cancelled."); return False
        stop_stack_guarded(robot, assume_yes=assume_yes, confirm=confirm, log=log)
        installer.Installer(root=robot.root).restore_factory(pkg_dir, manifest, log=log)
        log("Factory-restored. Power-cycle the robot (turn OFF, then ON) to activate.")
        return True
    finally:
        if cleanup:
            import shutil; shutil.rmtree(cleanup, ignore_errors=True)


# NOTE: no software reboot. On Unitree robots a soft `reboot` only cycles the
# Linux SoC (not the MCU/motors/power rail), so the stack comes back wrong — the
# user must power-cycle (physical off/on). app._power_cycle_notice() says so.
