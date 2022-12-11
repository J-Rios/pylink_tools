#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script:
    jklinkcontroller.py
Description:
    JLink Controller that ease usage of pylink for basic functionalities and
    communications with the debugger device and the target MCU connected
    through it.
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
### Imported modules

# Time Library
from datetime import datetime

# Logging Library
import logging

# Error Traceback Library
from traceback import format_exc

# Third-Party Libraries
import pylink

###############################################################################
### Logger Setup

logger = logging.getLogger(__name__)

###############################################################################
### Auxiliary JLink Controller Classes

class ConnectedJlink():
    '''Class Container for connected JLink information.'''
    product_name = ""
    serial_number = ""
    hw_version = ""
    fw_version = ""


class ConnectedMCU():
    '''Class Container for connected MCU target information.'''
    core = ""
    core_id = ""
    device_family = ""
    manufacturer = ""
    cpu_id = ""
    name = ""
    flash_size = ""
    ram_size = ""
    endianess = ""
    frequency = ""
    base_frequency = ""
    voltage = ""

###############################################################################
### JLink Controller Class

class JLinkController():
    '''
    Controller element that allow detection, connection and usage of
    JLink devices.
    '''

    def __init__(self):
        '''JLinkController Constructor.'''
        self.jlink = pylink.JLink()
        self.sdk_version = self.jlink.version
        self.detected_jlinks = []
        self.connected_jlink = ConnectedJlink()
        self.connected_mcu = ConnectedMCU()
        self.connected_jlink_serial_number = ""
        self.rtt_read_line = ""
        self.last_percentage = 0


    def show_sdk_info(self):
        logger.info("Pylink & Segger Toolchain Information:")
        logger.info("----------------------------")
        logger.info("Pylink Version: {}".format(pylink.__version__))
        logger.info("Segger Toolchain Version: {}\n".format(self.sdk_version))


    def discover(self):
        '''Detect and store a list of system connected JLink devices.'''
        self.detected_jlinks.clear()
        try:
            connected_probes = self.jlink.connected_emulators(
                    pylink.JLinkHost.USB)
        except Exception:
            logger.error(format_exc())
            logger.error("Fail system detection of JLinks\n")
            return False
        for probe in connected_probes:
            device = \
            {
                "product_name": probe.acProduct.decode(),
                "serial_number": probe.SerialNumber
            }
            if device not in self.detected_jlinks:
                self.detected_jlinks.append(device)
        if len(self.detected_jlinks) == 0:
            return False
        return True


    def is_any_jlink(self):
        '''Return if there is a JLink device detected in the system.'''
        return (len(self.detected_jlinks) > 0)


    def show_detected_jlinks(self):
        '''Show the list of discovered JLinks in the system.'''
        logger.info("List of JLinks devices detected:")
        logger.info("--------------------------------")
        if len(self.detected_jlinks) == 0:
            logger.info("No JLink debuggers found")
        else:
            i = 0
            for jlink in self.detected_jlinks:
                logger.info("{} - {} - {}".format(
                        i, jlink["product_name"], jlink["serial_number"]))
                i = i + 1
        logger.info("\n")


    def connect(self, jlink_serial_number):
        '''Make a connection to the provided JLink device.'''
        # Make the connection
        logger.info("Connecting to {} ...".format(jlink_serial_number))
        try:
            self.jlink.open(serial_no=jlink_serial_number)
            self.connected_jlink_serial_number = jlink_serial_number
        except Exception:
            logger.error(format_exc())
            logger.error("Fail connection to JLink\n")
            return False
        if not self.is_connected():
            logger.error("Fail connection to JLink: Something went wrong\n")
            return False
        logger.info("JLink Connected\n")
        # Get connected JLink info
        pn = self.jlink.product_name
        compiled_substring_index = pn.find(" compiled")
        if compiled_substring_index != -1:
            pn = pn[:compiled_substring_index]
        self.connected_jlink.product_name = pn
        if self.jlink.oem is not None:
            oem = self.jlink.oem
            self.connected_jlink.product_name = "{} {}".format(oem, pn)
        self.connected_jlink.serial_number = self.jlink.serial_number
        if self.connected_jlink.serial_number == -1:
            self.connected_jlink.serial_number = \
                    self.connected_jlink_serial_number
        self.connected_jlink.hw_version = self.jlink.hardware_version
        self.connected_jlink.fw_version = self.jlink.firmware_version
        # Disable JLink dialogs
        self.jlink.disable_dialog_boxes()
        self.jlink.exec_command("SuppressGUI")
        return True


    def show_jlink_info(self):
        '''Show Connected JLink Information.'''
        logger.info("Connected JLink Information:")
        logger.info("----------------------------")
        logger.info("Product Name: {}".format(
                self.connected_jlink.product_name))
        logger.info("Serial Number: {}".format(
                self.connected_jlink.serial_number))
        logger.info("HW Version: {}".format(
                self.connected_jlink.hw_version))
        logger.info("FW Version: {}\n".format(
                self.connected_jlink.fw_version))


    def is_connected(self):
        '''Return if connection to Jlink is done.'''
        return (self.jlink.opened() and self.jlink.connected())


    def connect_to_mcu(self, mcu_target, interface):
        '''Make a connection to the provided JLink device.'''
        # Set JLink-MCU communication interface to use
        interface = self.jlink_interface_from_string(interface)
        self.jlink.set_tif(interface)
        # Make the connection
        logger.info("Connecting to {} ...".format(mcu_target.upper()))
        try:
            self.jlink.connect(mcu_target)
        except Exception:
            logger.error(format_exc())
            logger.error("\nFail connection to MCU\n")
            return False
        if not self.is_mcu_connected():
            logger.error("\nFail connection to MCU: Something went wrong\n")
            return False
        logger.info("MCU Connected\n")
        # Get connected MCU info
        self.connected_mcu.core = self.jlink.core_name()
        self.connected_mcu.device_family = self.jlink.device_family()
        self.connected_mcu.cpu_id = self.jlink.core_cpu()
        self.connected_mcu.core_id = self.jlink.core_id()
        self.connected_mcu.frequency = self.jlink.cpu_speed()
        self.connected_mcu.base_frequency = self.jlink.speed_info.BaseFreq
        self.connected_mcu.manufacturer = self.jlink._device.manufacturer
        self.connected_mcu.name = self.jlink._device.name
        self.connected_mcu.voltage = self.jlink.hardware_status.VTarget
        self.connected_mcu.flash_size = self.jlink._device.FlashSize
        self.connected_mcu.ram_size = self.jlink._device.RAMSize
        if self.jlink._device.EndianMode != b'\x00':
            self.connected_mcu.endianess = "Big Endian"
        else:
            self.connected_mcu.endianess = "Little Endian"
        return True


    def show_mcu_target_info(self):
        '''Show current connected MCU target information.'''
        logger.info("Connected MCU Information:")
        logger.info("----------------------------")
        logger.info("MCU Name: {}".format(self.connected_mcu.name))
        logger.info("Manufacturer: {}".format(self.connected_mcu.manufacturer))
        logger.info("Core: {} ({})".format(
                self.connected_mcu.core, self.connected_mcu.core_id))
        logger.info("CPU ID: {}".format(self.connected_mcu.cpu_id))
        logger.info("Family: {}".format(self.connected_mcu.device_family))
        logger.info("Flash Size: {} KB".format(
                self.connected_mcu.flash_size / 1024))
        logger.info("RAM Size: {} KB".format(
                self.connected_mcu.ram_size / 1024))
        logger.info("Endianess: {}".format(self.connected_mcu.endianess))
        logger.info("Base Frequency: {} MHz".format(
                self.connected_mcu.base_frequency / 1000000))
        logger.info("Frequency: {} MHz".format(
                self.connected_mcu.frequency / 1000000))
        logger.info("Voltage: {} V\n".format(
                self.connected_mcu.voltage / 1000))


    def is_mcu_connected(self):
        '''Return if connection from JLink to target MCU is done.'''
        return self.jlink.target_connected()


    def is_jlink_mcu_connected(self):
        '''Return if connection to Jlink and MCU target is ok.'''
        return (self.is_connected() and self.is_mcu_connected())


    def fw_dump_file(self, file_path, address=0, length_to_read=None):
        '''Read MCU memory to dump it to an output firmware file.'''
        # Check if JLink is ready
        addr_hex_str = "0x{0:08X}".format(address)
        logger.info("Dumping from {} to FW file {} ...".format(
                addr_hex_str, file_path))
        if not self.is_jlink_mcu_connected():
            logger.info("[Error] Jlink/MCU is not ready")
            return False
        # Read memory
        if length_to_read is None:
            length_to_read = self.connected_mcu.flash_size
        try:
            fw_read_bytes = self.jlink.memory_read(address, length_to_read)
        except Exception:
            logger.error(format_exc())
            logger.error("Fail reading MCU memory\n")
            return False
        if len(fw_read_bytes) != length_to_read:
            logger.error("Read different number of bytes than expected")
            logger.error("Expected: {} bytes".format(length_to_read))
            logger.error("Read:     {} bytes\n".format(fw_read_bytes))
            return False
        # Write to file
        try:
            with open(file_path, "wb") as file_bin:
                file_bin.write(bytes(fw_read_bytes))
        except Exception:
            logger.error(format_exc())
            logger.error("Fail writing FW memory to file\n")
            return False
        logger.info("Memory dump success")
        return True


    def fw_flash_file(self, file_path, address, on_progress=None):
        '''
        Flash a Firmware file to the target MCU connected through JLink.
        '''
        bytes_written = 0
        if on_progress is None:
            on_progress = self.fw_flash_on_progress
        addr_hex_str = "0x{0:08X}".format(address)
        logger.info("Flasing to {} from FW file {} ...".format(
                addr_hex_str, file_path))
        if not self.is_jlink_mcu_connected():
            logger.info("[Error] Jlink/MCU is not ready")
            return False
        # Read binary file
        fw_data = None
        try:
            with open(file_path, "rb") as file:
                fw_data = file.read()
        except Exception:
            logger.error(format_exc())
            logger.error("Fail reading FW file\n")
            return False
        fw_bytes = list(fw_data)
        # Unlock MCU Read/Write access (only for some MCU families)
        try:
            self.jlink.unlock()
        except Exception:
            pass
        # Flash
        try:
            self.jlink.flash_file(file_path, address, on_progress=on_progress)
        except Exception:
            logger.error(format_exc())
            logger.error("Fail flashing FW file\n")
            return False
        # Read and verify written firmware
        try:
            read_bytes = self.jlink.memory_read(address, len(fw_bytes))
        except Exception:
            logger.error(format_exc())
            logger.error("Fail reading FW\n")
            return False
        if len(read_bytes) != len(fw_bytes):
            logger.error("Fail flashing firmware file: " \
                    "Verification missmatch\n")
            return False
        if read_bytes != fw_bytes:
            logger.error("Fail flashing firmware file: " \
                    "Verification missmatch\n")
            return False
        logger.info("Memory flash success")
        return True


    def fw_flash_on_progress(self, action, progress_string, percentage):
        '''Firmware file flashing progress callback.'''
        percentage = round(percentage)
        if percentage != self.last_percentage:
            logger.info("{} {}%".format(str(action, 'utf-8'), percentage))
            if progress_string is not None:
                logger.info(str(progress_string, 'utf-8'))
        self.last_percentage = percentage


    def rtt_start(self, logfile=None):
        '''Segger RTT debug mechanism initialization.'''
        logger.info("Starting RTT...\n")
        self.rtt_read_line = ""
        # Enable log to file if requested
        if logfile is not None:
            try:
                fh = logging.FileHandler(logfile)
                fh.setLevel(logging.INFO)
                logger.addHandler(fh)
            except Exception:
                logger.error(format_exc())
                logger.error("Fail to setup logging file")
        # Start RTT
        try:
            self.jlink.rtt_start()
        except Exception:
            logger.error(format_exc())
            logger.error("RTT Fail Init\n")
            return False
        return True


    def rtt_read(self, rtt_channel=0):
        '''Segger RTT debug mechanism message read.'''
        result_ok = False
        if not self.is_jlink_mcu_connected():
            return False
        try:
            read_byte = self.jlink.rtt_read(rtt_channel, 1)
            if read_byte:
                read_byte = "".join(map(chr, read_byte))
                if (read_byte != "\r") and (read_byte != "\n"):
                    self.rtt_read_line = self.rtt_read_line + read_byte
                if read_byte == "\n":
                    timestamp = self.get_timestamp()
                    text_line = self.rtt_read_line
                    if timestamp != "":
                        text_line = "{} {}".format(timestamp, text_line)
                    logger.info(text_line)
                    self.rtt_read_line = ""
            result_ok = True
        except Exception:
            logger.error(format_exc())
            logger.error("RTT Fail Read\n")
        return result_ok


    def rtt_write(self, data):
        '''Segger RTT debug mechanism message write.'''
        logger.info("RTT Write: {}".format(data))
        if not self.is_jlink_mcu_connected():
            logger.error("Jlink/MCU is not ready\n")
            return False
        try:
            data_bytes = list(bytearray(data, "utf-8") + b"\x0A\x00")
            bytes_written = self.jlink.rtt_write(0, data_bytes)
            if bytes_written != len(data_bytes):
                return False
        except Exception:
            #logger.error(format_exc())
            #logger.error("RTT Fail Write\n")
            return False
        return True


    def disconnect(self):
        '''Close the connection to JLink device.'''
        try:
            self.jlink.close()
            logger.info("JLink successfully disconnected\n")
        except Exception:
            logger.error(format_exc())
            logger.error("Fail to close JLink connection\n")
            return False
        return True


    def jlink_interface_from_string(self, interface):
        '''
        Get the corresponding JLink-MCU communication interface enum
        value, from a provided string.
        '''
        if interface is None:
            interface = ""
        interface = interface.lower()
        if interface == "swd":
            interface = pylink.enums.JLinkInterfaces.SWD
        elif interface == "jtag":
            interface = pylink.enums.JLinkInterfaces.JTAG
        elif interface == "icsp":
            interface = pylink.enums.JLinkInterfaces.ICSP
        elif interface == "spi":
            interface = pylink.enums.JLinkInterfaces.SPI
        elif interface == "fine":
            interface = pylink.enums.JLinkInterfaces.FINE
        elif interface == "c2":
            interface = pylink.enums.JLinkInterfaces.C2
        else:
            logger.warning("Invalid JLink-MCU interface, using SWD as default")
            interface = pylink.enums.JLinkInterfaces.SWD
        return interface


    def get_timestamp(self):
        '''Get current UTC time and create a timestamp string from it.'''
        timestamp = ""
        try:
            tobj = datetime.utcnow()
            timestamp = "[{}-{}-{} {}:{}:{}.{}]".format(
                    tobj.year, tobj.month, tobj.day, tobj.hour, tobj.minute,
                    tobj.second, "{}".format(tobj.microsecond)[:3])
        except Exception:
            logger.error(format_exc())
            logger.error("Fail to get current time and create timestamp\n")
        return timestamp
