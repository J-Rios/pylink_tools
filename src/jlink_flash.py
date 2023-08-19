#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script:
    jlink_flash.py
Description:
    This script connect to JLink target MCU and write the provided firmware
    file to the specified memory address.
Author:
    Jose Miguel Rios Rubio
Creation date:
    11/12/2022
Last modified date:
    11/12/2022
Version:
    1.0.0
'''

###############################################################################
### Script Name & Version

NAME = __file__
VERSION = "1.0.0"
DATE = "11/12/2022"

###############################################################################
### Imported modules

# Argument Parser Library
from argparse import ArgumentParser

# Logging Library
import logging

# Operating System Library
from os import path as os_path

# System Signals Library
from platform import system as os_system
from signal import signal, SIGTERM, SIGINT
if os_system() != "Windows":
    from signal import SIGUSR1

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

    OPT_DEVICE = \
        "Specify the target MCU to connect (i.e. stm32l431vc)"

    OPT_JLINK_SN = \
        "Specify the Serial Number of the JLink to use"

    OPT_INTERFACE = \
        "Specify the JLink interface protocol to use (i.e. swd, jtag, spi)"

    OPT_INPUT_FILE = \
        "Specify input file to flash the firmware"

    OPT_FLASH_ADDRESS = \
        "Specify MCU memory address to start writing the firmware file"

###############################################################################
### Auxiliary Application Functions

def auto_int(x):
    '''Integer conversion using automatic base detection.'''
    return int(x, 0)


def parse_options():
    '''Get and parse program input arguments.'''
    arg_parser = ArgumentParser()
    arg_parser.version = VERSION
    arg_parser.add_argument("-d", "--device", help=TEXT.OPT_DEVICE,
                            action='store', type=str, required=True)
    arg_parser.add_argument("-f", "--firmwarefile", help=TEXT.OPT_INPUT_FILE,
                            action='store', type=str, required=True)
    arg_parser.add_argument("-a", "--address", help=TEXT.OPT_FLASH_ADDRESS,
                            action='store', type=auto_int, default=0x08000000)
    arg_parser.add_argument("-s", "--serialnumber", help=TEXT.OPT_JLINK_SN,
                            action='store', type=str)
    arg_parser.add_argument("-i", "--interface", help=TEXT.OPT_INTERFACE,
                            action='store', type=str)
    arg_parser.add_argument("-v", "--version", action="version")
    args = arg_parser.parse_args()
    return vars(args)

###############################################################################
### Main Application Function

app_exit = False

def main(argc, argv):
    jlink = JLinkController()
    # Get arguments
    arg_options = parse_options()
    jlink_serial_number = arg_options["serialnumber"]
    mcu_target = arg_options["device"]
    jlink_mcu_interface = arg_options["interface"]
    fw_file = arg_options["firmwarefile"]
    address = arg_options["address"]
    # JLink Discovery
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
    # Connect to target
    if not jlink.connect_to_mcu(mcu_target, jlink_mcu_interface):
        jlink.disconnect()
        return
    # Show MCU Info
    jlink.show_mcu_target_info()
    # Flash firmware file to device memory
    if not jlink.fw_flash_file(fw_file, address):
        jlink.disconnect()
        return
    # Disconnect JLink
    logger.info("")
    jlink.disconnect()
    return 0

###############################################################################
### System Termination Signals Management

def system_termination_signal_handler(signal,  frame):
    '''Termination signals detection handler. It stop application execution.'''
    global app_exit
    app_exit = True


def system_termination_signal_setup():
    '''
    Attachment of System termination signals (SIGINT, SIGTERM, SIGUSR1) to
    function handler.
    '''
    # SIGTERM (kill pid) to signal_handler
    signal(SIGTERM, system_termination_signal_handler)
    # SIGINT (Ctrl+C) to signal_handler
    signal(SIGINT, system_termination_signal_handler)
    # SIGUSR1 (self-send) to signal_handler
    if os_system() != "Windows":
        signal(SIGUSR1, system_termination_signal_handler)

###############################################################################
### Runnable Main Script Detection

if __name__ == '__main__':
    logger.info("{} v{} {}\n".format(os_path.basename(NAME), VERSION, DATE))
    system_termination_signal_setup()
    return_code = main(len(sys_argv) - 1, sys_argv[1:])
    sys_exit(return_code)
