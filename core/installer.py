"""
installer.py — md5-gated, backup-first file install/restore engine.

Platform-agnostic: every destination path, expected patched md5 and expected
original (vanilla) md5 comes from the package manifest, so the same engine drives
R1/G1/Go2. It does file operations only — stopping services and rebooting are the
caller's (platform/feature) responsibility.

Safety model (per the design decisions):
  * NEVER patch a file whose current md5 is neither the known vanilla nor the
    known patched one (an unknown/foreign modification) unless force=True.
  * Back up the on-robot original to a NEW timestamped dir every time; nothing is
    ever overwritten, so any prior state can be restored.
  * Verify the destination md5 equals the expected patched md5 after copying.
"""
import json
import os
import time

from . import fsutil

# per-file preflight verdicts
VANILLA = "vanilla"        # dest == original_md5  -> safe to patch
INSTALLED = "installed"    # dest == patched_md5   -> already done, skip
MISSING = "missing"        # dest file absent
FOREIGN = "foreign"        # dest is some other md5 -> refuse unless force
BADPKG = "bad_package"     # the package's own patched file failed its md5


class InstallError(Exception):
    pass


class Installer:
    def __init__(self, root="", backup_base=None):
        # root is a sandbox prefix for testing/dry-run; "" means the real robot.
        self.root = root.rstrip("/")
        self.backup_base = backup_base or (self.root + "/unitree/.fwtools_backup")

    # ---- path helpers -------------------------------------------------------
    def _dest(self, entry):
        return self.root + entry["dest"]

    def _ordered(self, manifest):
        order = manifest.get("deploy_order") or [f["name"] for f in manifest["files"]]
        by_name = {f["name"]: f for f in manifest["files"]}
        return [by_name[n] for n in order if n in by_name]

    # ---- preflight ----------------------------------------------------------
    def preflight(self, pkg_dir, manifest):
        """Inspect the robot + package without changing anything.

        Returns a list of dicts: {name, dest, verdict, current_md5, patched_md5,
        original_md5, pkg_ok}. Read this before install() to show the user.
        """
        report = []
        for entry in self._ordered(manifest):
            patched_md5 = entry["patched"]["md5"]
            original_md5 = entry.get("original_md5")
            src = os.path.join(pkg_dir, entry["patched"]["path"])
            pkg_ok = fsutil.md5(src) == patched_md5
            cur = fsutil.md5(self._dest(entry))
            if not pkg_ok:
                verdict = BADPKG
            elif cur is None:
                verdict = MISSING
            elif cur == patched_md5:
                verdict = INSTALLED
            elif original_md5 and cur == original_md5:
                verdict = VANILLA
            else:
                verdict = FOREIGN
            report.append({
                "name": entry["name"], "dest": entry["dest"], "verdict": verdict,
                "current_md5": cur, "patched_md5": patched_md5,
                "original_md5": original_md5, "pkg_ok": pkg_ok,
                "patch_notes": entry.get("patch_notes", ""),
            })
        return report

    def status(self, manifest):
        """Per-file verdict using ONLY the manifest md5s (no package files needed).

        Good for the info card / quick 'is secondary-dev enabled?' check offline.
        Returns (all_installed, report).
        """
        report = []
        for entry in self._ordered(manifest):
            cur = fsutil.md5(self._dest(entry))
            patched_md5 = entry["patched"]["md5"]
            original_md5 = entry.get("original_md5")
            if cur is None:
                verdict = MISSING
            elif cur == patched_md5:
                verdict = INSTALLED
            elif original_md5 and cur == original_md5:
                verdict = VANILLA
            else:
                verdict = FOREIGN
            report.append({"name": entry["name"], "dest": entry["dest"],
                           "verdict": verdict, "current_md5": cur})
        all_installed = bool(report) and all(r["verdict"] == INSTALLED for r in report)
        return all_installed, report

    # ---- install ------------------------------------------------------------
    def install(self, pkg_dir, manifest, force=False, dry_run=False, log=print):
        """Back up + replace every file. Returns (backup_dir, results)."""
        pf = self.preflight(pkg_dir, manifest)
        bad = [r for r in pf if r["verdict"] == BADPKG]
        if bad:
            raise InstallError("package integrity check failed for: "
                               + ", ".join(r["name"] for r in bad))
        foreign = [r for r in pf if r["verdict"] == FOREIGN]
        if foreign and not force:
            raise InstallError(
                "refusing to patch files with an unrecognized md5 (not vanilla, not "
                "our patch): " + ", ".join(r["name"] for r in foreign)
                + ".\nBack them up/restore factory first, or re-run with force=True.")

        ts = time.strftime("%Y%m%d-%H%M%S")
        backup_dir = os.path.join(self.backup_base, ts)
        backup_files = []
        results = []

        for entry, r in zip(self._ordered(manifest), pf):
            name = entry["name"]
            dest = self._dest(entry)
            if r["verdict"] == INSTALLED:
                log(f"  = {name:20s} already installed, skipping")
                results.append({"name": name, "action": "skipped"})
                continue

            mode = fsutil.parse_mode(entry.get("mode", "0644"))
            if dry_run:
                log(f"  ~ {name:20s} would back up + install (verdict={r['verdict']})")
                results.append({"name": name, "action": "dry-run"})
                continue

            # 1) back up the current on-robot file (if present)
            if r["current_md5"] is not None:
                fsutil.ensure_dir(backup_dir)
                bpath = os.path.join(backup_dir, name)
                cur_mode = fsutil.file_mode(dest)
                fsutil.copy_preserving_mode(dest, bpath, mode=cur_mode)
                backup_files.append({
                    "name": name, "dest": entry["dest"], "md5": r["current_md5"],
                    "mode": oct(cur_mode) if cur_mode is not None else None,
                    "verdict_at_backup": r["verdict"],
                })
                log(f"  ↑ {name:20s} backed up ({r['current_md5'][:8]}…)")

            # 2) install the patched file
            src = os.path.join(pkg_dir, entry["patched"]["path"])
            applied_mode = fsutil.copy_preserving_mode(src, dest, mode=mode)
            # 3) verify
            got = fsutil.md5(dest)
            if got != entry["patched"]["md5"]:
                raise InstallError(f"{name}: post-install md5 mismatch "
                                   f"(got {got}, want {entry['patched']['md5']})")
            log(f"  ✓ {name:20s} installed + verified (mode {oct(applied_mode)})")
            results.append({"name": name, "action": "installed"})

        # write the backup manifest so restore is self-describing
        if backup_files:
            fsutil.ensure_dir(backup_dir)
            with open(os.path.join(backup_dir, "backup_manifest.json"), "w") as f:
                json.dump({
                    "created": ts,
                    "package_id": manifest.get("package_id"),
                    "robot": manifest.get("robot"),
                    "files": backup_files,
                }, f, indent=2)
        return (backup_dir if backup_files else None), results

    # ---- backups / restore --------------------------------------------------
    def list_backups(self):
        out = []
        if not os.path.isdir(self.backup_base):
            return out
        for ts in sorted(os.listdir(self.backup_base), reverse=True):
            mpath = os.path.join(self.backup_base, ts, "backup_manifest.json")
            if os.path.isfile(mpath):
                with open(mpath) as f:
                    out.append({"ts": ts, "dir": os.path.dirname(mpath), "manifest": json.load(f)})
        return out

    def restore_backup(self, backup, log=print):
        """Restore originals recorded in a backup dict (from list_backups)."""
        bm = backup["manifest"]
        bdir = backup["dir"]
        for fe in bm["files"]:
            src = os.path.join(bdir, fe["name"])
            dest = self.root + fe["dest"]
            if not os.path.isfile(src):
                log(f"  ! {fe['name']:20s} backup file missing, skipping")
                continue
            mode = fsutil.parse_mode(fe["mode"]) if fe.get("mode") else None
            fsutil.copy_preserving_mode(src, dest, mode=mode)
            got = fsutil.md5(dest)
            ok = got == fe["md5"]
            log(f"  {'✓' if ok else '!'} {fe['name']:20s} restored"
                + ("" if ok else f" but md5 mismatch (got {got})"))
        return True

    def restore_factory(self, pkg_dir, manifest, log=print):
        """Restore the vanilla files shipped in the package's factory/ tree.

        Used when there is no local backup (e.g. the robot was already modified
        before the tool ever ran). Requires has_factory packages.
        """
        if not manifest.get("has_factory"):
            raise InstallError("this package has no factory/ originals to restore from")
        for entry in self._ordered(manifest):
            fac = entry.get("factory")
            if not fac:
                continue
            src = os.path.join(pkg_dir, fac["path"])
            if fsutil.md5(src) != fac["md5"]:
                raise InstallError(f"factory file for {entry['name']} failed md5 check")
            dest = self._dest(entry)
            mode = fsutil.parse_mode(entry.get("mode", "0644"))
            fsutil.copy_preserving_mode(src, dest, mode=mode)
            got = fsutil.md5(dest)
            ok = got == fac["md5"]
            log(f"  {'✓' if ok else '!'} {entry['name']:20s} factory-restored"
                + ("" if ok else f" but md5 mismatch (got {got})"))
        return True


def load_manifest(path):
    with open(path) as f:
        m = json.load(f)
    if m.get("schema") != 1 or "files" not in m:
        raise InstallError(f"unrecognized manifest schema in {path}")
    return m
