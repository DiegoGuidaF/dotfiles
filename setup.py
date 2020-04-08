#!/bin/env python3

import logging
import sys
import os
import argparse
import yaml
import subprocess
from colorama import Fore
from colorama import Style

LOGGER = logging.getLogger(__name__)
DEPENDENCIES_YAML = './dependencies.yml'
PACMAN_INST_CMD = ['yay', '-S','--needed']
HOME = os.path.expanduser('~')
# --dotfiles option allows interpreting folders/files with 'dot-' prefix as starting with . when symlinking.
STOW_CMD = ['stow', '-vRt', HOME]

def arg_parser():
    parser = argparse.ArgumentParser(description="Install and configure packages from dotfiles managed via Stow.")
    parser.add_argument('packages', type=str, metavar='packages', nargs='+', help='Package names as seen in their folder name.')
    args = parser.parse_args()
    return args

def init_logger():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
            '%(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.DEBUG)

def logging_color(message, color):
    LOGGER.info(f'{color}{message}{Style.RESET_ALL}')

def read_dependencies():
    with open(DEPENDENCIES_YAML) as f:
        dependencies = yaml.load(f, Loader=yaml.FullLoader)

    return dependencies

def main():
    init_logger()
    args = arg_parser()
    packages_folders = os.listdir()
    dependencies = read_dependencies()['packages']
    # TODO: Print all available packages, also check that all folders have a package in the depend files.
    # Print could be by listing them and highlighting those chosen, then ask for confirm or add more without exiting.
    packages_to_install = {'arch':[], 'aur':[], 'conf_required':[]}

    logging_color(f'Packages to install: {args.packages}', Fore.YELLOW)
    for package in args.packages:
        logging_color(f'Checking dependencies for {package}...', Fore.YELLOW)
        p_dependencies = dependencies.get(package, {})
        packages_to_install['arch'].extend(p_dependencies.get('arch',[]))
        packages_to_install['aur'].extend(p_dependencies.get('aur',[]))
        LOGGER.debug(f'{package} dependencies {p_dependencies}.')
        # If extra configuration files are present...
        if package in packages_folders:
            packages_to_install['conf_required'].append(package)
            LOGGER.debug(f'{package} Configuration files found.')
    logging_color(f'Oficial repo dependencies:\n{packages_to_install["arch"]}', Fore.LIGHTGREEN_EX)
    logging_color(f'Aur dependencies:\n{packages_to_install["aur"]}', Fore.LIGHTGREEN_EX)
    logging_color(f'Packages with configuration:\n{packages_to_install["conf_required"]}', Fore.GREEN)

    # TODO: Parse option to enable installing packages, don't install by default until so...
    #logging_color('Installing required dependencies...', Fore.YELLOW)
    #cmd = PACMAN_INST_CMD.copy()
    #cmd.extend(packages_to_install['arch'])
    #cmd.extend(packages_to_install['aur'])
    #subprocess.call(cmd)
    logging_color('Copying configuration files...', Fore.YELLOW)
    for package in packages_to_install['conf_required']:
        logging_color(f'Configuring {package}...', Fore.YELLOW)
        cmd = STOW_CMD.copy()
        cmd.append(package)
        subprocess.call(cmd)

if __name__ == "__main__":
    logging_color("REVIEW SCRIPT BEFORE EXECUTING!",Fore.RED)
    exit
    main()
