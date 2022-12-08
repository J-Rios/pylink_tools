#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script:
    jlink_list.py
Description:
    This script shows a list of connected JLinks devices detected by the
    system.
Author:
    Jose Miguel Rios Rubio
Creation date:
    08/12/2022
Last modified date:
    08/12/2022
Version:
    1.0.0
'''

###############################################################################
### Script Name & Version

NAME = __file__
VERSION = "1.0.0"
DATE = "08/12/2022"

###############################################################################
### Imported modules

# Operating System Library
from os import path as os_path

# System Library
from sys import argv as sys_argv
from sys import exit as sys_exit

# Logging Library
import logging

# Third-Party Libraries
from jlinkcontroller import JLinkController

###############################################################################
### Logger Setup

logging.basicConfig(
    #format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    format="%(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

###############################################################################
### Main Application Function

def main(argc, argv):
    jlink = JLinkController()
    jlink.discover()
    jlink.show_detected_jlinks()
    return 0

###############################################################################
### Runnable Main Script Detection

if __name__ == '__main__':
    #logger.info("{} v{} {}\n".format(os_path.basename(NAME), VERSION, DATE))
    logger.info("")
    return_code = main(len(sys_argv) - 1, sys_argv[1:])
    sys_exit(return_code)
