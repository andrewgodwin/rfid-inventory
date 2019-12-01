import struct

from .base import Command, Response
from ..constants import COMMAND, STATUS
from ..exceptions import NoTagError


class ReaderInformationResponse(Response):
    """
    Contains information about the reader
    """

    symbol = COMMAND.GET_READER_INFORMATION

    def decode_data(self):
        (
            self.major_version,
            self.minor_version,
            self.reader_type,
            self.protocol_type,
            max_frequency_byte,
            min_frequency_byte,
            self.power,
            self.scan_time,
        ) = struct.unpack("<BBBBBBBB", self.data)

    def __repr__(self):
        return "<%s version:%s.%s power:%s scantime:%s>" % (
            self.__class__.__name__,
            self.major_version,
            self.minor_version,
            self.power,
            self.scan_time,
        )


class GetReaderInformation(Command):
    """
    Requests current reader status information.
    """

    response_class = ReaderInformationResponse

    def __init__(self):
        super().__init__(command=COMMAND.GET_READER_INFORMATION)


class SetRegion(Command):
    """
    Sets the region of the reader to a predetermined value.
    """

    regions = {
        "usa": ""
    }

    def __init__(self, region):
        try:
            region_details = self.regions[region]
        except KeyError:
            raise ValueError("%s is not a valid region" % region)
        super().__init__(command=COMMAND.SET_REGION, data=struct.pack("<B", power))


class SetScanTime(Command):
    """
    Sets the scan time for inventory commands, in seconds.
    """
    def __init__(self, scan_time):
        scan_time_hundreds_ms = int(scan_time * 10)
        if 3 <= scan_time_hundreds_ms <= 255:
            super().__init__(command=COMMAND.SET_SCAN_TIME, data=struct.pack("<B", scan_time_hundreds_ms))
        else:
            raise ValueError("Scan time %s is out of range" % scan_time)


class SetPower(Command):
    """
    Sets the power output.
    """
    def __init__(self, power):
        super().__init__(command=COMMAND.SET_POWER, data=struct.pack("<B", power))


class AcoustoOpticControl(Command):
    """
    Alows flashing of the LED/buzzer.

    Pass time values in s.
    """
    def __init__(self, active_time=0, silent_time=0, repeat=0):
        active_time = int(active_time * 20)
        silent_time = int(silent_time * 20)
        if 0 <= active_time <= 255 and 0 <= silent_time <= 255 and 0 < repeat < 255:
            super().__init__(command=COMMAND.ACOUSTO_OPTIC_CONTROL, data=struct.pack("<BBB", active_time, silent_time, repeat))
        else:
            raise ValueError("Values out of range")
