#!/usr/bin/python
import os
import argparse
import subprocess as sp
import logging
import i3ipc
import re
logger = logging.getLogger(__name__)
LOG_FILE = 'workspace.log'

HOME = os.path.expanduser("~")
#dmenu with rofi:
rofi_dmenu_cmd = [HOME+'/bin/launch_rofi.sh']

sway = i3ipc.Connection()

def arg_parser():
    parser = argparse.ArgumentParser(description="Control workspaces for Sway")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--go', '-g', nargs='?', const='default', type=str, action='store', help='Launch dmenu to select WS, if not exists create it.')
    group.add_argument('--switch', '-s', type=int, help='Switch to WS by number')
    group.add_argument('--move', '-m', nargs='?', const='default', type=str, action='store', help='Move WS to selected output')
    group.add_argument('--runInWs', '-r',action='store_true', help='Run application in a workspace of the same name')
    args = parser.parse_args()
    return args

def init_logger():
    # Stream handler
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
            '%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # File handler
    f_handler = logging.FileHandler(LOG_FILE)
    f_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_formatter)
    logger.addHandler(f_handler)

    logger.setLevel(logging.DEBUG)

def check_ws_exists(ws_name):
    pattern = re.compile("^[0-9]\.")
    for ws in sway.get_workspaces():
        logger.info(f'{ws.name}')
        # Remove number from workspaces so we get only the name
        if pattern.match(ws_name):
            ws_name = ws_name.split(".")[1]
        if pattern.match(ws.name):
            ws.name = ws.name.split(".")[1]
        if ws.name == ws_name:
            logger.debug(f'Current ws {ws.name} selected is {ws_name}')
            return True
    return False

def generate_ws_name(ws_name):
    num = get_available_ws_number()
    return f'{num}.{ws_name}'

def go_to_ws(ws_name, cmd):
    logger.info(f'Go to {ws_name}')
    if not check_ws_exists(ws_name):
        ws_name = generate_ws_name(ws_name)
        logger.info(f'Creating workspace {ws_name}')
    else:
        logger.info(f'Workspace {ws_name} already present, no need to create it')

    logger.debug(f'Cmd is \'{cmd.format(ws_name)}\'')
    if ws_name:
        sway.command(cmd.format(ws_name))

def get_available_ws_number():
    workspaces = sway.get_workspaces()
    ws_numbers = [ws.num for ws in workspaces]
    # Remove all occurrences of -1 from list
    [ws_numbers.remove(-1) for x in range(ws_numbers.count(-1))]
    # Convert to set and back to list to remove duplicated items
    ws_numbers = list(set(ws_numbers))
    ws_numbers.sort()
    logger.debug(f'Current WS numbers are {ws_numbers}')
    # Get the next number available, ensu
    for pos,num in enumerate(ws_numbers,1):
        if pos is not num:
            logger.debug(f'Skipped number found {pos}')
            next_number = pos
            break
        # If we have reached the end of the current ws,
        # number is the next one.
        elif pos == len(ws_numbers):
            next_number = pos + 1
            logger.debug(f'All numbers present, first non used number is {next_number}')

    return next_number

def list_ws_get_option():
    workspaces = sway.get_workspaces()
    ws_list = [ ws.name for ws in workspaces]
    dmenu_input = '\n'.join(ws_list)
    
    try:
        cmd_run = sp.run(rofi_dmenu_cmd + ["-dmenu"], capture_output=True, check=True, text=True,input=dmenu_input)
        # Get output and strip trailing line jump     
        chosen_ws = cmd_run.stdout.rstrip('\n')
        return chosen_ws
    except sp.CalledProcessError:
        logger.error(f'Failed executing {cmd_run.args}')

def run_app_in_own_ws():
    rofi_cmd = rofi_dmenu_cmd + ["-show", "drun", "-run-command","echo {cmd}"]
    app_cmd = sp.run(rofi_cmd, capture_output=True, check=True, text=True).stdout.rstrip('\n')
    DESKTOP_FILES_LOCATIONS = ["/usr/share/applications",f"{HOME}/.local/share/applications"]
    RG_CMD = ["rg","-Lg","!mimeinfo.cache"]

    # Command to find desktop file containing the chosen app so that we can find an user-friendly name
    # to set as WS name.
    #Note: Using ripgrep since it is way faster (compiled and optimized for this)
    get_app_name_cmd = RG_CMD + ["-Fli", app_cmd] + DESKTOP_FILES_LOCATIONS

    desktop_file_name = sp.run(get_app_name_cmd, capture_output=True, check=True, text=True).stdout.rstrip('\n')
    logger.debug(f"Desktop file is {desktop_file_name}")

    # Find the name field (sometimes just Name, others with en_GB (could be en_US, check if this happens)
    get_friendly_name = RG_CMD + ["^Name=|^Name\\[en_GB\\]=",desktop_file_name]
    app_name_line = sp.run(get_friendly_name, capture_output=True, check=True, text=True).stdout.rstrip('\n')

    #TODO: Limit number of characters if found annoying
    app_name = app_name_line.split("\n")[0].split("=")[1].replace(" ","")

    # Add the number of the next WS
    ws_name = generate_ws_name(app_name)
    logger.info(f"WS name is {ws_name}")

    # Start the app in a new workspace.
    # TODO: Find if possible to not go to WS when starting, so that we can start in the background
    start_app_in_ws_cmd = ["swaymsg",f"workspace {ws_name}; exec {app_cmd}"]
    sp.run(start_app_in_ws_cmd, check=True)

def switch_to_prev_ws():
    switch_prev_ws_cmd = ["swaymsg","workspace", "back_and_forth"]
    sp.run(switch_prev_ws_cmd, check=True)

def main():
    init_logger()
    args = arg_parser()
    logger.debug(args)
    if args.go:
        logger.info(f"Launching dmenu to get WS name.")
        chosen_ws = list_ws_get_option()
        logger.info(f"Chosen ws name is {chosen_ws}")
        go_to_ws(chosen_ws, 'workspace {}' )
    elif args.move:
        logger.info(f"Launching dmenu to get WS name.")
        chosen_ws = list_ws_get_option()
        logger.info(f"Chosen ws name is {chosen_ws}")
        go_to_ws(chosen_ws,'move container to workspace {}')
    elif args.runInWs:
        logger.info(f"Running application in WS of same name.")
        run_app_in_own_ws()

if __name__ == "__main__":
    main()
