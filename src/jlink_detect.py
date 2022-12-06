#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script:
    jlink_detect.py
Description:
    This script allows to verify that a JLink device is detected by the system 
    and can be used through the Segger Toolchain (works properly).
    It checks and shows a list of connected JLinks devices (showing their
    Serial Number), and then try connection to the first one detected to get
    and show information from it.
Author:
    Jose Miguel Rios Rubio
Creation date:
    06/12/2022
Last modified date:
    06/12/2022
Version:
    1.0.0
'''

###############################################################################
### Script Name & Version

NAME = __file__
VERSION = "1.0.0"
DATE = "06/12/2022"

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
    logger.info("{} v{} {}\n".format(os_path.basename(NAME), VERSION, DATE))
    # Create JLink Controller
    jlink = JLinkController()
    # Show Segger SDK Toolchain and Pylink Version Info
    jlink.show_sdk_info()
    # Detect and show a list of connected JLinks
    if not jlink.discover():
        return 1
    jlink.show_detected_jlinks()
    if not jlink.is_any_jlink():
        return 0
    # Connect to each of the JLinks and show it info
    for jlink_to_connect in jlink.detected_jlinks:
        if not jlink.connect(jlink_to_connect):
            logger.info("Can't connect to {} ({})".format(
                    jlink_to_connect["product_name"],
                    jlink_to_connect["serial_number"]))
            continue
        jlink.show_jlink_info()
        # CLose JLink
        jlink.disconnect()
    return 0

###############################################################################
### Runnable Main Script Detection

if __name__ == '__main__':
    sys_exit(main(len(sys_argv) - 1, sys_argv[1:]))
