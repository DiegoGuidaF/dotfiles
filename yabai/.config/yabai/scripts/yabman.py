#!/bin/env python
import os
import json
import subprocess
import argparse
import logging

logger = logging.getLogger(__name__)
LOG_FILE = 'workspace.log'
HOME = os.path.expanduser("~")

CHOOSE_CMD = ['choose', '-m']
YABAI_CMD = ['yabai', '-m']

def init_logger():
    # Stream handler
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
            '%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # File handler
    f_handler = logging.FileHandler(HOME+ '/' + LOG_FILE)
    f_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_formatter)
    logger.addHandler(f_handler)

    logger.setLevel(logging.DEBUG)


def arg_parser():
    parser = argparse.ArgumentParser(description="Control workspaces for yabai")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--go-space', '-gs', nargs='?', const='default', type=str, action='store', help='Launch choose to select WS, if not exists create it.')
    group.add_argument('--go-window', '-gw', nargs='?', const='default', type=str, action='store', help='Launch choose to select window, if not exists create it.')
    #group.add_argument('--switch', '-s', type=int, help='Switch to WS by number')
    #group.add_argument('--move', '-m', nargs='?', const='default', type=str, action='store', help='Move WS to selected output')
    #group.add_argument('--runInWs', '-r',action='store_true', help='Run application in a workspace of the same name')
    args = parser.parse_args()
    logger.debug("Args are: {}".format(args))

    return args


        
class Yabman:

    def __init__(self):
        pass

    def _get_windows(self):
        return self._query_cmd("windows")

    def _get_spaces(self):
        return self._query_cmd("spaces")

    def _query_cmd(self, cmd):
        res = subprocess.run(
                YABAI_CMD + ['query', f'--{cmd}'],
                capture_output=True).stdout.decode()
        res = json.loads(res)
        return res

    def _choose_from_options(self, options):
        chosen_option = subprocess.run(
                CHOOSE_CMD,
                input=options,
                encoding='utf',
                capture_output=True).stdout
        logger.info(f"Chosen ws name is {chosen_option}")
        return chosen_option

    def _parse_spaces_names(self, spaces):
        spaces_names = []
        for space in spaces:
            spaces_names.append("{index}.{label}".format(**space))
        logger.debug(f"Available spaces: {spaces_names}")
        return spaces_names

    def _parse_windows_names(self, windows):
        windows_names = []
        for window in windows:
            windows_names.append("{app} || {title} || {id}".format(**window))
        logger.debug(f"Available windows: {windows_names}")
        return windows_names

    def choose_space(self, spaces):
        spaces_list = ""
        parsed_spaces = self._parse_spaces_names(spaces)
        for space_name in parsed_spaces:
            spaces_list += space_name + '\n'

        return self._choose_from_options(spaces_list)

    def choose_window(self, windows):
        windows_list = ""
        parsed_windows = self._parse_windows_names(windows)
        for window_name in parsed_windows:
            windows_list += window_name + '\n'

        return self._choose_from_options(windows_list)

    def focus_space(self, space_name):
        space_name = space_name.split('.')[1]
        subprocess.run(
                YABAI_CMD + ['space', '--focus', space_name],
                capture_output=True).stdout.decode()
        logger.info(f"Focused space {space_name}")

    def focus_window(self, window_name):
        window_id = window_name.split('||')[2].strip()
        subprocess.run(
                YABAI_CMD + ['window', '--focus', window_id],
                capture_output=True).stdout.decode()
        logger.info(f"Focused window {window_id}")

    def run(self, args):
        if args.go_space:
            spaces = self._get_spaces()
            logger.info(f"Launching choose to get WS name.")
            chosen_space = self.choose_space(spaces)
            self.focus_space(chosen_space)

        elif args.go_window:
            windows = self._get_windows()
            logger.info(f"Launching choose to get window name.")
            chosen_window = self.choose_window(windows)
            self.focus_window(chosen_window)


if __name__ == "__main__":

    init_logger()
    args = arg_parser()

    yb = Yabman()

    yb.run(args)
