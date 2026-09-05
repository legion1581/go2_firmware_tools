# Unitree Firmware Tools

Unitree's **AIR** and **PRO** robots ship with **secondary development locked** — you can't
freely send low-level commands or drive the robot from the SDK. That's a shame. **This is the
repo that fixes it:** it safely **re-enables secondary development**, so you can use your robot
with any SDK — official or unofficial.

Run it on the robot (or deploy from a host). It reads the robot's real model/edition, applies an
md5-verified patch package (with timestamped backups so you can always roll back), and installs a
**guardian** failsafe that keeps you from being locked out.

> ⚠️ **Root access is required first.** This tool configures a robot that is **already
> jailbroken (root)** — it does *not* jailbreak the robot for you. Do the jailbreak first;
> see the **RoboLegion Discord** for the guide → [robolegion.com](https://robolegion.com).

## ⚠️ Disclaimer

Modifying robot firmware carries risk. **Use this only on a robot you personally own.** You do so
**entirely at your own risk** — the author accepts **no responsibility for any damage, injury, or
loss** resulting from its use.

## Supported

| Robot | Status |
|---|---|
| **R1** | ✅ supported — firmware **1.4.2** |
| **G1** | 🚧 on the way |
| **Go2** | 🚧 on the way |

More R1 firmware versions plus G1 / Go2 support are coming.

## Run

On the robot (you're already root after the jailbreak), just:

```bash
./start.sh                          # auto-detects the robot, shows the info card + menu
```

`start.sh` passes options through to `app.py`, so for advanced use:

```bash
./start.sh --platform R1
./start.sh --package /path/to/secondary_dev_r1_1.4.2.zip    # install offline
```

**Menu**
- **Robot info** — model/edition, serial, region, hardware, firmware, secondary-dev + guardian status.
- **Secondary development** — Status / Enable / Restore backup / Restore factory.
  - *Enable* requires the guardian (auto-offered), downloads + verifies the package against its `manifest.json`, refuses to touch any file whose md5 isn't the known-vanilla one, **stops the running stack the OTA way** (`mscli stopservice …` + `master_service`, behind a motion-safety confirm on R1/G1), backs up each original to `/unitree/.fwtools_backup/<timestamp>/`, installs + re-verifies, then reboots.
  - *Restore backup* — reinstalls the exact originals saved before patching (pick a timestamp if several exist). Fully offline.
  - *Restore factory* — reinstalls the vanilla files from the package's `factory/` tree, ignoring backups (needs the package: download or `--package`).
- **Guardian failsafe** — install/remove the `unitree-guardian` systemd service (see below).

## Guardian failsafe (`unitree-guardian`)

An independent systemd service (never depends on the stack it guards). Every few seconds it:
1. keeps `sshd` alive despite `net-init`'s `systemctl disable ssh`;
2. **keeps root loginable across OTA updates** — re-applies the root password (default `robolegion`) and re-enables root SSH login whenever an update resets them;
3. snapshots the last-known-good WiFi while the stack is healthy;
4. if `master_service` fails to boot (or WiFi drops), restores that WiFi + `sshd` — with a `/unitree`-independent fallback (`wpa_supplicant@wlan0` / `hostapd`) for when the whole stack is broken.

Tunables via env (`GUARDIAN_ROOT_PW`, `GUARDIAN_KEEP_ROOT_PW`, `GUARDIAN_KEEP_ROOT_SSH`, `GUARDIAN_BOOT_GRACE`, `GUARDIAN_POLL`).

## Updating the official firmware (OTA)

**Restore before you update.** If you plan to run an official OTA update, first put the robot
back to stock — **Secondary development → Restore backup** (or **Restore factory**). Patched
binaries can make the OTA **fail**, so always restore first, update, then re-enable afterwards.

The **guardian** is also your safety net *across* an OTA. An OTA typically **changes the root
password and disables SSH**, which would lock you out — the guardian re-applies your password and
keeps SSH enabled. And if the Unitree stack fails to boot after an update, the guardian brings up
**WiFi** so you can still get in.

## R1: wired connection required

On the **R1** the SDK/DDS traffic only works over **Ethernet**, and the robot has no spare
Ethernet jack — so you add one with a small **JST → RJ45 adapter** on the empty Lidar port. See
**[docs/R1_ETHERNET.md](docs/R1_ETHERNET.md)** for the adapter pinout. The robot is then reachable
at **192.168.123.161** from any secondary-development PC (laptop, SBC, …).

## Deploy from a host

```bash
ROBOT=root@192.168.123.161 ./deploy.sh        # rsync to /unitree/dev/unitree_firmware_tools
./deploy.sh --run                              # deploy then launch over ssh
```

Or install on the robot directly:
```bash
mkdir -p /unitree/dev && cd /unitree/dev
git clone https://github.com/legion1581/unitree_firmware_tools.git
cd unitree_firmware_tools && pip install -r requirements.txt
./start.sh
```

## Layout
`core/` (yandex download, md5-gated install/backup engine, OTA-style `service_control`),
`platforms/` (R1/G1/Go2 identity + paths), `features/` (info, secondary_dev, supervisor),
`assets/` (guardian service + `service_stop/` OTA order + bundled manifests).
The R1 patch package is built by `secondary_development_patch/package_r1.py` → `out/r1/`.

### Thanks
To the RoboLegion community! Visit [robolegion.com](https://robolegion.com) for info and support.

### Support
If you like this project, consider buying me a coffee:

<a href="https://www.buymeacoffee.com/legion1581" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
