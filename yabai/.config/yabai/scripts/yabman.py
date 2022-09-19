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

class YabaiClient:
    def __init__(self):
        pass

    # Something weird happening after refactor!
    def _query_cmd(self, cmd):
        res = self._yabai_cmd(['query', f'--{cmd}'])
        return json.loads(res.stdout.decode())

    def _focus_cmd(self, cmd, entity_id):
        self._yabai_cmd([cmd, '--focus', f'{entity_id}'])

    #def _change_space_display(self, space, display):

    def _yabai_cmd(self, params):
        res = subprocess.run(
                YABAI_CMD + params,
                capture_output=True)
        if res.stderr:
            logger.error(f"error found: {res.stderr}")
            exit
        return res

class Windows(YabaiClient):
    """
    Sample output for a single window
    {"id":4145, "pid":44531, "app":"Vivaldi", "title":"Session expired - Vivaldi", 
            "frame":{ "x":481.0000, "y":565.0000, "w":1279.0000, "h":875.0000 },
        "role":"AXWindow", "subrole":"AXStandardWindow", "tags":"0x0300000000080409", "display":1, "space":6, "level":0,
        "opacity":1.0000, "split-type":"vertical", "stack-index":0, "can-move":true, "can-resize":true, "has-focus":false,
        "has-shadow":false, "has-border":false, "has-parent-zoom":false, "has-fullscreen-zoom":false, "is-native-fullscreen":false,
        "is-visible":false, "is-minimized":false, "is-hidden":false, "is-floating":false, "is-sticky":false, "is-topmost":false,
        "is-grabbed":false
    }}
    """
    def __init__(self):
        self.windows = self._query_cmd("windows")
        self._add_friendlyNames()

    def _add_friendlyNames(self):
        for window in self.windows:
            window["friendlyName"] = "{app} || {title}".format(**window)

    def focus(self, window):
        self._focus_cmd("window", window["id"])
        logger.info(f'Focused window {window["friendlyName"]}')

    def get(self):
        return self.windows

class Spaces(YabaiClient):
    def __init__(self):
        self.spaces = self._query_cmd("spaces")
        self._add_friendlyNames()

    def _add_friendlyNames(self):
        for space in self.spaces:
            space["friendlyName"] = "{label}".format(**space)

    def focus(self, space):
        self._focus_cmd("space", space["index"])
        logger.info(f'Focused space {space["friendlyName"]}')


    def get(self):
        return self.spaces
        
class Yabman:

    def __init__(self):
        pass


    def _choose_entity(self, entities):
        choose_options = "\n".join([option["friendlyName"] for option in entities])
        logger.info(f"Launching choose to get WS name.")

        # TODO: Manage case were chose window is closen with ESC
        chosen_option_index = int(subprocess.run(
                CHOOSE_CMD + ["-i"],
                input=choose_options,
                encoding='utf',
                capture_output=True).stdout)
        logger.info(f"Chosen element is {entities[chosen_option_index]}")
        return entities[chosen_option_index]

    def go_to_space(self):
        spaces = Spaces()
        chosen_space = self._choose_entity(spaces.get())
        spaces.focus(chosen_space)

    def go_to_window(self):
        windows = Windows()
        chosen_window = self._choose_entity(windows.get())
        windows.focus(chosen_window)

    def run(self, args):
        if args.go_space:
            self.go_to_space()

        elif args.go_window:
            self.go_to_window()


if __name__ == "__main__":

    init_logger()
    args = arg_parser()

    yb = Yabman()

    yb.run(args)
