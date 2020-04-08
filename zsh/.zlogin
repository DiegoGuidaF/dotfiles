# This file is sourced AFTER zshrc
if systemctl -q is-active graphical.target && [[ ! $DISPLAY && $XDG_VTNR -eq 1 ]]; then
  exec launch_sway.sh
fi

