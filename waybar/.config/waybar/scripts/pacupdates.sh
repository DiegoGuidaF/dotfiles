#!/bin/bash
set -e
readonly updates="$(checkupdates)"
num_updates="$(echo -n "$updates" | wc -l)"
if [[ $num_updates == 0 ]]; then
    num_updates=""
    class="updated"
else
    class="pending updates"
fi
alt="$class"
tooltip=$(echo "$updates" | sed -z 's/\n/\\n/g')

echo '{"text": "'$num_updates'", "tooltip": "'${tooltip::-2}'", "class": "'$class'", "alt":"'$alt'"}'
