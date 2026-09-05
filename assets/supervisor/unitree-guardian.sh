#!/bin/sh
# unitree-guardian — lock-out failsafe for R1/G1 (installed by unitree_firmware_tools).
#
# Runs as an independent systemd service (does NOT depend on the services it guards)
# and, every few seconds:
#   1. keeps sshd alive despite net-init's "systemctl disable ssh" (re-enables it),
#   2. keeps root lognable: maintains the root password (default robolegion) and
#      PermitRootLogin/PasswordAuthentication in sshd_config — an OTA rewrites
#      /etc/shadow + sshd_config wholesale, which would otherwise lock you out,
#   3. snapshots the last-known-good WiFi while the stack is healthy, and
#   4. if master_service fails to come up (or the WiFi link drops), re-applies that
#      last-known-good WiFi + ensures sshd — even when /unitree itself is broken
#      (direct wpa_supplicant/hostapd fallback) — so a bad patch can't lock you out.
#
# Touch-free w.r.t. service binaries: only sshd + root creds + WIFI_MODE + wifi
# scripts, none of which trip master's integrity gate.
set -u

LOG=/var/log/unitree-guardian.log
STASH=/var/lib/unitree-guardian
WIFI_MODE_FILE=/unitree/etc/wifi/WIFI_MODE
WPA_CONF=/etc/wpa_supplicant/wpa_supplicant-wlan0.conf
HOSTAPD_CONF=/etc/hostapd/hostapd.conf
SSHD_CONF=/etc/ssh/sshd_config
SHADOW=/etc/shadow

# --- credentials to keep working across OTA shadow/sshd_config rewrites --------
ROOT_USER=${GUARDIAN_ROOT_USER:-root}
ROOT_PW=${GUARDIAN_ROOT_PW:-robolegion}
KEEP_ROOT_PW=${GUARDIAN_KEEP_ROOT_PW:-1}       # 0 to disable password maintenance
KEEP_ROOT_SSH=${GUARDIAN_KEEP_ROOT_SSH:-1}     # 0 to leave sshd_config alone

BOOT_GRACE=${GUARDIAN_BOOT_GRACE:-150}      # s to let the stack come up before judging it failed
POLL=${GUARDIAN_POLL:-8}
LINK_FAIL_MAX=${GUARDIAN_LINK_FAIL_MAX:-8}  # * POLL s of no wlan0 carrier -> restore wifi

mkdir -p "$STASH"
log() { echo "$(date '+%F %T') $*" >>"$LOG" 2>/dev/null; }

# --- sshd ---------------------------------------------------------------------
ensure_ssh() {
    systemctl is-active --quiet ssh 2>/dev/null && return 0
    systemctl reset-failed ssh 2>/dev/null
    systemctl enable ssh 2>/dev/null      # essential: net-init runs `systemctl disable ssh`
    systemctl start ssh 2>/dev/null
    pgrep -x sshd >/dev/null 2>&1 || /usr/sbin/sshd 2>/dev/null
    log "ssh was down -> (re)enabled + started"
}

# Keep root SSH login possible (OTA can reset PermitRootLogin/PasswordAuthentication).
ensure_sshd_root_login() {
    [ "$KEEP_ROOT_SSH" = "1" ] || return 0
    [ -f "$SSHD_CONF" ] || return 0
    changed=0
    for kv in "PermitRootLogin yes" "PasswordAuthentication yes"; do
        key=${kv%% *}
        if grep -qiE "^[#[:space:]]*${key}[[:space:]]" "$SSHD_CONF"; then
            cur=$(grep -iE "^[[:space:]]*${key}[[:space:]]" "$SSHD_CONF" | tail -1 | awk '{print $2}')
            [ "$cur" = "yes" ] && continue
            sed -i "s/^[#[:space:]]*${key}[[:space:]].*/${kv}/I" "$SSHD_CONF"; changed=1
        else
            echo "$kv" >>"$SSHD_CONF"; changed=1
        fi
    done
    if [ "$changed" = "1" ]; then
        log "sshd_config root-login (re)applied"
        systemctl reload ssh 2>/dev/null || systemctl restart ssh 2>/dev/null
    fi
}

# Keep root's password = $ROOT_PW. Only writes /etc/shadow when it actually changed
# (OTA rewrote it), by comparing the live root hash against the last one we set.
ensure_root_pw() {
    [ "$KEEP_ROOT_PW" = "1" ] || return 0
    command -v chpasswd >/dev/null 2>&1 || return 0
    cur=$(grep "^${ROOT_USER}:" "$SHADOW" 2>/dev/null | cut -d: -f2)
    [ -n "$cur" ] || return 0
    want=$(cat "$STASH/root.hash" 2>/dev/null || echo "")
    if [ "$cur" != "$want" ]; then
        if echo "${ROOT_USER}:${ROOT_PW}" | chpasswd 2>/dev/null; then
            grep "^${ROOT_USER}:" "$SHADOW" | cut -d: -f2 > "$STASH/root.hash" 2>/dev/null
            passwd -u "$ROOT_USER" >/dev/null 2>&1   # unlock if OTA left it locked
            log "root password (re)applied (shadow changed / first run)"
        fi
    fi
}

# --- stack / wifi -------------------------------------------------------------
stack_ok() { pgrep -x master_service >/dev/null 2>&1 && pgrep -f '/basic_service' >/dev/null 2>&1; }
wlan_up()  { [ "$(cat /sys/class/net/wlan0/carrier 2>/dev/null)" = "1" ]; }
nm_script() { ls /unitree/module/network_manager/*/upper_bluetooth/"$1" 2>/dev/null | head -1; }

save_wifi() {
    [ -f "$WIFI_MODE_FILE" ] && cp -f "$WIFI_MODE_FILE" "$STASH/WIFI_MODE" 2>/dev/null
    [ -f "$WPA_CONF" ]     && cp -f "$WPA_CONF"     "$STASH/wpa.conf"     2>/dev/null
    [ -f "$HOSTAPD_CONF" ] && cp -f "$HOSTAPD_CONF" "$STASH/hostapd.conf" 2>/dev/null
    touch "$STASH/.saved"
}

# Bring wifi up WITHOUT /unitree — used when the whole stack is broken/absent.
restore_wifi_standalone() {
    mode=$(cat "$STASH/WIFI_MODE" 2>/dev/null || cat "$WIFI_MODE_FILE" 2>/dev/null || echo STA)
    log "wifi standalone fallback (mode=$mode, /unitree scripts unavailable)"
    rfkill unblock wifi 2>/dev/null
    ip link set wlan0 up 2>/dev/null
    if [ "$mode" = "AP" ]; then
        systemctl restart hostapd 2>/dev/null || \
            { pkill -x hostapd 2>/dev/null; [ -f "$HOSTAPD_CONF" ] && hostapd -B "$HOSTAPD_CONF" 2>/dev/null; }
    else
        systemctl restart wpa_supplicant@wlan0 2>/dev/null || \
            { pkill -x wpa_supplicant 2>/dev/null
              [ -f "$WPA_CONF" ] && wpa_supplicant -B -i wlan0 -c "$WPA_CONF" 2>/dev/null; }
        # get an address (netplan, then dhclient/udhcpc, whichever exists)
        netplan apply 2>/dev/null || dhclient wlan0 2>/dev/null || udhcpc -i wlan0 2>/dev/null
    fi
}

restore_wifi() {
    [ -f "$STASH/.saved" ] || { log "no last-known-good wifi saved yet; ensuring ssh only"; return 1; }
    log "restoring last-known-good wifi"
    [ -f "$STASH/WIFI_MODE" ]    && cp -f "$STASH/WIFI_MODE"    "$WIFI_MODE_FILE" 2>/dev/null
    [ -f "$STASH/wpa.conf" ]     && cp -f "$STASH/wpa.conf"     "$WPA_CONF"       2>/dev/null
    [ -f "$STASH/hostapd.conf" ] && cp -f "$STASH/hostapd.conf" "$HOSTAPD_CONF"   2>/dev/null
    wi=$(nm_script wifi_init.sh)
    if [ -n "$wi" ]; then
        sh "$wi" 2>/dev/null
    else  # /unitree wifi scripts gone (broken stack) -> stand-alone bring-up
        mode=$(cat "$WIFI_MODE_FILE" 2>/dev/null)
        if [ "$mode" = "AP" ]; then
            ap=$(nm_script ap_connect/ap_connect.sh);  [ -n "$ap" ] && sh "$ap" -r 2>/dev/null || restore_wifi_standalone
        else
            wp=$(nm_script wpa_connect/wpa_connect.sh); [ -n "$wp" ] && sh "$wp" -i wlan0 -r 2>/dev/null || restore_wifi_standalone
        fi
    fi
}

fallback_done=0
linkfail=0
log "guardian start (boot_grace=${BOOT_GRACE}s poll=${POLL}s keep_root_pw=${KEEP_ROOT_PW} keep_root_ssh=${KEEP_ROOT_SSH})"
while :; do
    ensure_ssh
    ensure_sshd_root_login
    ensure_root_pw
    uptime_s=$(cut -d. -f1 /proc/uptime 2>/dev/null || echo 0)

    if stack_ok; then
        fallback_done=0
        wlan_up && save_wifi
    elif [ "$uptime_s" -ge "$BOOT_GRACE" ] && [ "$fallback_done" = "0" ]; then
        log "master_service not healthy (uptime ${uptime_s}s) -> restore wifi + ssh"
        restore_wifi
        ensure_ssh
        fallback_done=1
    fi

    if wlan_up; then
        linkfail=0
    else
        linkfail=$((linkfail + 1))
        if [ "$linkfail" -ge "$LINK_FAIL_MAX" ]; then
            log "wlan0 no carrier for ~$((linkfail * POLL))s -> restore wifi"
            restore_wifi
            linkfail=0
        fi
    fi

    sleep "$POLL"
done
