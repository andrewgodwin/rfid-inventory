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
        reader.send_raw(self.address, self.command, self.data)
        try:
            tags = []
            # Get raw data
            address, command, status, data = reader.receive_raw()
            assert status in (STATUS.INVENTORY_OK, STATUS.INVENTORY_TIMEOUT)
            # TODO: Handle the case where there's extra response messages with more tags
            # Decode tags
            number_of_tags = struct.unpack("<B", data[:1])[0]
            data = data[1:]
            for i in range(number_of_tags):
                epc_length = struct.unpack("<B", data[:1])[0]
                tags.append("".join(
                    "%02x" % byte
                    for byte in data[1:epc_length + 1]
                ))
                data = data[epc_length + 1:]
            assert not data
            # Create response instance
            return InventoryResponse(address, command, status, tags)
        except NoTagError:
            # Create empty response
            return InventoryResponse(self.address, self.command, STATUS.ERROR_NO_TAG, [])


class InventoryResponse(Response):
    """
    Handles decoding data properly, and also potentially errors or multiple returns.
    """

    def __init__(self, address, command, status, tags):
        super().__init__(address, command, status, None)
        self.tags = tags

    def __repr__(self):
        return "<%s %s tags>" % (
            self.__class__.__name__,
            len(self.tags)
        )
