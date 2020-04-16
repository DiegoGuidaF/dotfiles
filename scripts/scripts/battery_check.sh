#!/bin/bash
set -o pipefail

readonly BAT_LVL_WARN=15
readonly BAT_LVL_CRITICAL=3
BATTINFO=`acpi -b`
NOTIFY_SEND_CMD="notify-send -u critical -t 0 -a battery_check"
# File used to check if we have already warned about low battery,
# this way we only warn the first time.
NOTIFY_CACHE_FILE="/tmp/battery_check_notified"

current_bat_level="$(echo $BATTINFO | grep "Discharging" | grep -oe "[0-9]*%" | sed 's/%//g')"
echo "Battery level is at $current_bat_level. Warn/Crit - $BAT_LVL_WARN/$BAT_LVL_CRITICAL"


# Battery CRITICAL
if [[ $current_bat_level -le $BAT_LVL_CRITICAL ]] ; then
    # Below command may fail if sway is not running, ignore
    swaymsg fullscreen disable >/dev/null
    $NOTIFY_SEND_CMD -i /usr/share/icons/Arc/status/symbolic/battery-empty-symbolic.svg \
        "Battery Critical!" "Charge at $current_bat_level%\nSuspending system..."
    #systemctl hybrid-sleep
    exit 0
fi

# Battery WARNING
if [[ $current_bat_level -le $BAT_LVL_WARN && ! -f $NOTIFY_CACHE_FILE ]] ; then
    # Below command may fail if sway is not running, ignore
    swaymsg fullscreen disable >/dev/null
    $NOTIFY_SEND_CMD -i /usr/share/icons/Arc/status/symbolic/battery-caution-symbolic.svg \
        "Battery warning" "Charge at $current_bat_level%\n"
    touch $NOTIFY_CACHE_FILE
    exit 0
elif [[ $current_bat_level -gt $BAT_LVL_WARN && -f $NOTIFY_CACHE_FILE ]]; then
    echo "Battery warning removed"
    rm $NOTIFY_CACHE_FILE
fi
