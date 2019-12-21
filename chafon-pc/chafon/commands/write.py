import struct

from .base import Command, Response
from ..constants import COMMAND, STATUS


class WriteEPC(Command):
    """
    Writes the EPC of a single, random tag in the field.
    """

    def __init__(self, epc):
        # Verify the EPC is a whole number of 16-bit words
        raw_epc = bytes.fromhex(epc)
        assert raw_epc and len(raw_epc) % 2 == 0, "EPC is not a whole number of 16-bit words"
        # Construct the data - first, length of write and password
        data = struct.pack("<BI", len(raw_epc)//2, 0)
        # Add in the EPC
        data += raw_epc
        # Write it
        super().__init__(
            command=COMMAND.WRITE_EPC,
            data=data,
        )
