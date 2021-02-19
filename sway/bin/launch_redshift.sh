#!/bin/bash
set -x
readonly PROGRAM="gammastep"
readonly PID="$(pidof $PROGRAM)"
readonly PROCESS_STATUS=$(pidof $PROGRAM>/dev/null && echo "active" || echo "inactive")

if [[ $1 == "status" ]]; then
    class=$PROCESS_STATUS
    alt=$class
    # Text field is empty since Icon is decided on "alt". Text would be only if we would like showing
    # something else.
    echo "{\"text\": \"$text\", \"tooltip\": \"$tooltip\", \"class\": \"$class\", \"alt\":\"$alt\"}"
elif [[ $1 == "toggle" ]]; then
    if [[ $PROCESS_STATUS == "active" ]]; then
        kill $PID&>/dev/null
        # Wait until process is stopped since it takes time
        tail --pid=$PID -f /dev/null
    else
        exec $PROGRAM&>/dev/null&
    fi
else
    echo 'Wrong arguments'
    exit 1
fi

exit 0
