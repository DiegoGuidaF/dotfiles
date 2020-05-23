#!/bin/bash

exec sway  2>&1 >sway.log #| systemd-cat -t sway -p info
