#!/bin/bash
# Turns off system services that a virtual server of the olympiad does not use, to free memory.
# By default it only SHOWS the state; --apply turns them off. Nothing is uninstalled.
#
#   sudo bash slim_services.sh            # show
#   sudo bash slim_services.sh --apply
#   sudo systemctl unmask <unit> && sudo systemctl enable --now <unit>     # turn one back on
set -u
APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1
[ "$APPLY" = 0 ] || [ "$(id -u)" = 0 ] || { echo "run with sudo"; exit 2; }
# ModemManager: no modems. multipathd: one virtual disk. fwupd: no firmware to update in a VM.
# udisks2: no removable disks. snapd: no snap programs are used. motd-news, apport: desktop extras.
UNITS="ModemManager.service multipathd.socket multipathd.service fwupd-refresh.timer fwupd.service
       udisks2.service snapd.socket snapd.service snapd.snap-repair.timer motd-news.timer
       apport-autoreport.timer"
if grep -qE '(/dev/mapper/mpath|multipath)' /etc/fstab || ls /dev/mapper/mpath* >/dev/null 2>&1; then
    echo "multipath disks are in use here, multipathd stays on"
    UNITS=$(echo $UNITS | sed 's/multipathd\.s[a-z]*//g')
fi
for unit in $UNITS; do
    systemctl cat "$unit" >/dev/null 2>&1 || continue
    echo "$unit: $(systemctl is-active "$unit"), $(systemctl is-enabled "$unit" 2>/dev/null)"
    [ "$APPLY" = 1 ] || continue
    systemctl disable --now "$unit" >/dev/null 2>&1
    # mask: these are also started on demand by other programs.
    systemctl mask "$unit" >/dev/null 2>&1 && echo "    turned off"
done
[ "$APPLY" = 1 ] || echo "(dry run: nothing changed, add --apply)"
