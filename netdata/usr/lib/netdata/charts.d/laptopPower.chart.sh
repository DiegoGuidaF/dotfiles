# shellcheck shell=bash
# no need for shebang - this file is loaded from charts.d.plugin
# SPDX-License-Identifier: GPL-3.0-or-later

# netdata
# real-time performance and health monitoring, done right!
#

# if this chart is called X.chart.sh, then all functions and global variables
# must start with X_

# _update_every is a special variable - it holds the number of seconds
# between the calls of the _update() function
laptopPower_update_every=

# the priority is used to sort the charts on the dashboard
# 1 = the first chart
laptopPower_priority=150000

# to enable this chart, you have to set this to 12345
# (just a demonstration for something that needs to be checked)
laptopPower_magic_number=

# global variables to store our collected data
# remember: they need to start with the module name laptopPower_
laptopPower_charge=
laptopPower_discharge=
laptopPower_power_file="/sys/class/power_supply/BAT0/power_now"
laptopPower_power_status_file="/sys/class/power_supply/BAT0/status"

laptopPower_get() {
  # do all the work to collect / calculate the values
  # for each dimension
  laptopPower_charge=0
  laptopPower_discharge=0
  #
  # Remember:
  # 1. KEEP IT SIMPLE AND SHORT
  # 2. AVOID FORKS (avoid piping commands)
  # 3. AVOID CALLING TOO MANY EXTERNAL PROGRAMS
  # 4. USE LOCAL VARIABLES (global variables may overlap with other modules)

  local laptopPower_value=$(<$laptopPower_power_file)
  if cat $laptopPower_power_status_file | grep -q "Charging"; then
    laptopPower_charge="$laptopPower_value"
  elif cat $laptopPower_power_status_file | grep -q "Discharging"; then
    laptopPower_discharge="-$laptopPower_value"
  fi

  # this should return:
  #  - 0 to send the data to netdata
  #  - 1 to report a failure to collect the data

  return 0
}

# _check is called once, to find out if this chart should be enabled or not
laptopPower_check() {
  # check that we can collect data
  laptopPower_get || return 1

  return 0
}

# _create is called once, to create the charts
laptopPower_create() {
  # create the chart with 3 dimensions
  cat << EOF
CHART laptop.power '' "Laptop power draw" "W" power laptop.power area $((laptopPower_priority)) $laptopPower_update_every
DIMENSION laptop_charge charge absolute  1 1000000
DIMENSION laptop_discharge discharge absolute  1 1000000
EOF

  return 0
}

# _update is called continuously, to collect the values
laptopPower_update() {
  # the first argument to this function is the microseconds since last update
  # pass this parameter to the BEGIN statement (see bellow).

  laptopPower_get || return 1

  # write the result of the work.
  cat << VALUESEOF
BEGIN laptop.power $1
SET laptop_charge = $laptopPower_charge
SET laptop_discharge = $laptopPower_discharge
END
VALUESEOF

  return 0
}
