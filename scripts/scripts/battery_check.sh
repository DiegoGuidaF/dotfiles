#!/bin/bash
set -o pipefail
set -e

readonly BAT_LVL_WARN=15
readonly BAT_LVL_CRITICAL=3

readonly BATTINFO_FULL=`acpi -b`
echo -e "BATTERY_DEBUG:\n$BATTINFO_FULL"

# System keeps adding a Battery 1 seemingly randomly, so that sometimes
# we have two batteries reported by "acpi -b". Only way to know
# which one is the correct one is by grepping the "remaining" key word
# since it seems to only be reported by the valid one.
readonly BATTINFO=$(echo "$BATTINFO_FULL"| grep "remaining")
readonly NOTIFY_SEND_CMD="notify-send -u critical -t 0 -a battery_check"
# File used to check if we have already warned about low battery,
# this way we only warn the first time.
readonly NOTIFY_CACHE_FILE="/tmp/battery_check_notified"

case $(echo $BATTINFO | awk '{print $3}' | sed s/,//) in
    "Charging")
        echo "Battery is charging, not doing anything..."
        exit 0
        ;;
    "Discharging")
        echo "Battery is Discharging"
        ;;
    *)
        echo "Battery Unknown state!"
        echo $BATTINFO
        exit 0
        ;;

esac

# Validate and accept only numbers here.
current_bat_level="$(echo $BATTINFO | grep -e "Discharging" -e "Battery $BATT_NUMBER" | grep -oe "[0-9]*%" | sed 's/%//g')"
echo "Battery level is at "$current_bat_level". Warn/Crit - $BAT_LVL_WARN/$BAT_LVL_CRITICAL"

if [ -z "$current_bat_level" ]; then
    echo "Invalid battery level received, acpi reported: $BATTINFO"
    exit 1
fi

# TODO: Add option to warn each 2% of battery lost
if [[ $current_bat_level -le $BAT_LVL_WARN \
    && $current_bat_level -gt $BAT_LVL_CRITICAL \
    && ! -f $NOTIFY_CACHE_FILE ]]; then
    # Below command may fail if sway is not running, ignore
    swaymsg fullscreen disable >/dev/null
    $NOTIFY_SEND_CMD -i /usr/share/icons/Arc/status/symbolic/battery-caution-symbolic.svg \
        "Battery warning" "Charge at $current_bat_level%\n"
    echo $current_bat_level > $NOTIFY_CACHE_FILE
    echo "Battery level low, warn issued"
    exit 0
# Battery CRITICAL
elif [[ $current_bat_level -le $BAT_LVL_CRITICAL ]] ; then
    # Below command may fail if sway is not running, ignore
    swaymsg fullscreen disable >/dev/null
    $NOTIFY_SEND_CMD -i /usr/share/icons/Arc/status/symbolic/battery-empty-symbolic.svg \
        "Battery Critical!" "Charge at $current_bat_level%\nSuspending system..."
    echo "Battery level CRITICAL, suspending system..."
    systemctl hybrid-sleep
    exit 0
elif [[ $current_bat_level -gt $BAT_LVL_WARN 
    && -f $NOTIFY_CACHE_FILE ]]; then
    echo "Battery level not critical now, warning cache removed"
    rm $NOTIFY_CACHE_FILE
fi
