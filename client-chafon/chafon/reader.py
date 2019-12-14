import serial
import struct
from crcmod.predefined import Crc

from .constants import STATUS, TYPES
from .exceptions import *


class Reader:
    """
    Class that represents a reader
    """

    def __init__(self, device, baud=57600, type="ru5102"):
        self.connection = serial.Serial(device, baud)
        assert type in TYPES
        self.type = type

    def send_raw(self, address, command, data):
        """
        Sends a command to the device.
        """
        # Packet header
        packet = struct.pack("<BBB", len(data) + 4, address, command)
        # Packet data
        packet += data
        # CRC
        crc16 = Crc("crc-16-mcrf4xx")
        crc16.update(packet)
        packet += struct.pack("<H", crc16.crcValue)
        self.connection.write(packet)

    def receive_raw(self):
        """
        Receives a response and returns the raw values
        """
        length_byte = self.connection.read(1)
        length = struct.unpack("<B", length_byte)[0]
        packet = self.connection.read(length)
        # Check the CRC checksum
        crc16 = Crc("crc-16-mcrf4xx")
        crc16.update(length_byte + packet[:-2])
        packet_crc = struct.unpack("<H", packet[-2:])[0]
        if crc16.crcValue != packet_crc:
            raise RuntimeError(
                "Bad CRC checksum on response: %s != %s" % (crc16.crcValue, packet_crc)
            )
        # Unpack main values
        address, command, status = struct.unpack("<BBB", packet[:3])
        data = packet[3:-2]
        # Check for errors
        if status == STATUS.ERROR_COMMAND_EXECUTE:
            raise CommandExecutionError()
        if status == STATUS.ERROR_POOR_COMMS:
            raise PoorCommunicationError()
        if status == STATUS.ERROR_NO_TAG:
            raise NoTagError()
        if status == STATUS.ERROR_COMMAND_LENGTH:
            raise CommandLengthWrong()
        if status == STATUS.ERROR_TAG_INTERNAL:
            raise InternalTagError(struct.unpack("<B", data)[0])
        if status == STATUS.ERROR_ILLEGAL_COMMAND:
            raise IllegalCommand()
        if status == STATUS.ERROR_PARAMETER:
            raise ParameterError()
        # Return raw data
        return address, command, status, data

    def run(self, command):
        return command.run(self)
