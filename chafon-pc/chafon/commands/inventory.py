import struct

from .base import Command, Response
from ..constants import COMMAND, STATUS
from ..exceptions import NoTagError


class Inventory(Command):
    """
    Asks for current EPC tags in view.
    """

    def __init__(self):
        super().__init__(command=COMMAND.INVENTORY)

    def run(self, reader):
        """
        Handles no tag/multiple returns
        """
        if reader.type == "rru2881":
            # Use the extended-parameters format
            self.data = struct.pack(
                "<BB",
                0x04,  # Q value  (roughly 0.5 * tag quantity),
                0xFF,  # Session (auto)
            )
        reader.send_raw(self.address, self.command, self.data)
        try:
            tags = set()
            while True:
                # Get raw data
                address, command, status, data = reader.receive_raw()
                assert status in (
                    STATUS.INVENTORY_OK,
                    STATUS.INVENTORY_TIMEOUT,
                    STATUS.INVENTORY_MORE_DATA,
                ), ("Bad status %02x" % status)
                # Decode tags
                if reader.type == "rru2881":
                    tags.update(self.decode_tags_rssi(data))
                else:
                    tags.update(self.decode_tags_basic(data))
                if status != STATUS.INVENTORY_MORE_DATA:
                    break
            # Create response instance
            return InventoryResponse(address, command, status, tags)
        except NoTagError:
            # Create empty response
            return InventoryResponse(
                self.address, self.command, STATUS.ERROR_NO_TAG, []
            )

    def decode_tags_basic(self, data):
        """
        Decodes a returned set of tags without RSSI/antenna
        """
        tags = []
        number_of_tags = struct.unpack("<B", data[:1])[0]
        data = data[1:]
        for i in range(number_of_tags):
            epc_length = struct.unpack("<B", data[:1])[0]
            tags.append("".join("%02x" % byte for byte in data[1 : epc_length + 1]))
            data = data[epc_length + 1 :]
        assert not data
        return tags

    def decode_tags_rssi(self, data):
        """
        Decodes a returned set of tags without RSSI/antenna
        """
        tags = []
        antenna, number_of_tags = struct.unpack("<BB", data[:2])
        data = data[2:]
        for i in range(number_of_tags):
            epc_length = struct.unpack("<B", data[:1])[0]
            tags.append("".join("%02x" % byte for byte in data[1 : epc_length + 1]))
            data = data[
                epc_length + 2 :
            ]  # Last byte is the RSSI, which we ignore for now
        assert not data
        return tags


class InventoryResponse(Response):
    """
    Handles decoding data properly, and also potentially errors or multiple returns.
    """

    def __init__(self, address, command, status, tags):
        super().__init__(address, command, status, None)
        self.tags = tags

    def __repr__(self):
        return "<%s %s tags>" % (self.__class__.__name__, len(self.tags))
