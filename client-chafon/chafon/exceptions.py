class ReaderError(Exception):
    pass


class CommandExecutionError(ReaderError):
    pass


class PoorCommunicationError(ReaderError):
    pass


class NoTagError(ReaderError):
    pass


class InternalTagError(ReaderError):
    pass


class CommandLengthWrong(ReaderError):
    pass


class IllegalCommand(ReaderError):
    pass


class ParameterError(ReaderError):
    pass
