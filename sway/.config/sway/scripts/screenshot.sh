#!/bin/bash
FOLDER="$HOME/Pictures/Screenshots"
FILENAME="screenshot-`date +%F-%T`"

[ -d $FOLDER ] || mkdir -p $FOLDER

# Save screenshot to file and also copy it to clipboard
grim -g "$(slurp)" - | tee $FOLDER/$FILENAME.png | wl-copy
