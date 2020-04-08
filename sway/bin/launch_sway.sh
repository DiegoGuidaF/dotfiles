#!/bin/bash

exec sway 1>/dev/null 2>&1| systemd-cat -t sway -p info
