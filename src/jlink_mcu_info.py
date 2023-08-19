#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script:
    jlink_mcu_info.py
Description:
    This script allows to verify that a JLink device is detected by the system
    and can be used through the Segger Toolchain to connect into a target MCU
    (works properly).
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

# Argument Parser Library
from argparse import ArgumentParser

# Logging Library
import logging

# Operating System Library
from os import path as os_path

# System Library
from sys import argv as sys_argv
from sys import exit as sys_exit

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
### Texts

class TEXT():

    OPT_JLINK_SN = \
        "Specify the Serial Number of the JLink to use"

    OPT_INTERFACE = \
        "Specify the JLink interface protocol to use (i.e. swd, jtag, spi)"

    OPT_DEVICE = \
        "Specify the target MCU to connect (i.e. stm32l431vc)"

###############################################################################
### Auxiliary Application Functions

def parse_options():
    '''Get and parse program input arguments.'''
    arg_parser = ArgumentParser()
    arg_parser.version = VERSION
    arg_parser.add_argument("-d", "--device", help=TEXT.OPT_DEVICE,
                            action='store', type=str, required=True)
    arg_parser.add_argument("-s", "--serialnumber", help=TEXT.OPT_JLINK_SN,
                            action='store', type=str)
    arg_parser.add_argument("-i", "--interface", help=TEXT.OPT_INTERFACE,
                            action='store', type=str)
    arg_parser.add_argument("-v", "--version", action="version")
    args = arg_parser.parse_args()
    return vars(args)

###############################################################################
### Main Application Function

def main(argc, argv):
    jlink = JLinkController()
    arg_options = parse_options()
    jlink_serial_number = arg_options["serialnumber"]
    mcu_target = arg_options["device"]
    jlink_mcu_interface = arg_options["interface"]
    # JLink Discovery
    jlink.show_sdk_info()
    if not jlink.discover():
        logger.error("No JLink device detected in the system")
        return
    # Default to first detected JLink if Serial Number was not provided
    if jlink_serial_number is None:
        jlink_serial_number = jlink.detected_jlinks[0]["serial_number"]
        logger.warning("No JLink Serial Number specified, using first " \
                "detected device ({})".format(jlink_serial_number))
    # Connect to JLink
    if not jlink.connect(jlink_serial_number):
        return
    jlink.show_jlink_info()
    # Connect to target
    if not jlink.connect_to_mcu(mcu_target, jlink_mcu_interface):
        jlink.disconnect()
        return
    # Show MCU Info
    jlink.show_mcu_target_info()
    # Disconnect JLink
    jlink.disconnect()
    return 0

###############################################################################
### Runnable Main Script Detection

if __name__ == '__main__':
    logger.info("{} v{} {}\n".format(os_path.basename(NAME), VERSION, DATE))
    return_code = main(len(sys_argv) - 1, sys_argv[1:])
    sys_exit(return_code)
