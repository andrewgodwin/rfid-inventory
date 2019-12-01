class Response:
    """
    Represents a response from the reader
    """

    def __init__(self, address, command, status, data=None):
        self.command = command
        self.address = address
        self.status = status
        self.data = data or b""
        self.decode_data()

    @classmethod
    def run(cls, reader):
        """
        Parses the response from the given reader. Assumes command was already sent.
        """
        address, command, status, data = reader.receive_raw()
        return cls(address, command, status, data)

    def decode_data(self):
        """
        Hook for subclasses.
        """
        pass

    def __repr__(self):
        return "<%s cmd:%02x status:%02x>" % (
            self.__class__.__name__,
            self.command,
            self.status,
        )

class Command:
    """
    Basic unit of control for a reader.

    Has a reader address (default is 0), a command symbol,
    optional data, and a CRC.
    """

    response_class = Response

    def __init__(self, command, address=0, data=None):
        self.command = command
        self.address = address
        self.data = data or b""

    def run(self, reader):
        """
        Runs the packet via the given reader and returns the result as a Response class.
        """
        reader.send_raw(self.address, self.command, self.data)
        address, command, status, data = reader.receive_raw()
        if command != self.command:
            raise ValueError("Received response for wrong command (expected %02x, got %02x)" % (self.command, command))
        return self.response_class(address, command, status, data)
