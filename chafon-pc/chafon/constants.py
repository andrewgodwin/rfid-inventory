class COMMAND:
    INVENTORY = 0x01
    READ_DATA = 0x02
    WRITE_DATA = 0x03
    WRITE_EPC = 0x04
    KILL_TAG = 0x05
    LOCK = 0x06
    BLOCK_ERASE = 0x07
    READ_PROTECT = 0x08
    READ_PROTECT_WITHOUT_EPC = 0x09
    RESET_READ_PROTECT = 0x0A
    CHECK_READ_PROTECT = 0x0B
    EAS_ALARM = 0x0C
    CHECK_EAS_ALARM = 0x0D
    BLOCK_LOCK = 0x0E
    INVENTORY_SINGLE = 0x0F
    BLOCK_WRITE = 0x10
    # ISO18000-6B Commands
    INVENTORY_SINGLE_6B = 0x50
    INVENTORY_MULTIPLE_6B = 0x51
    READ_DATA_6B = 0x52
    WRITE_DATA_6B = 0x53
    CHECK_LOCK_6B = 0x54
    LOCK_6B = 0x55
    # Reader Commands
    GET_READER_INFORMATION = 0x21
    SET_REGION = 0x22
    SET_ADDRESS = 0x24
    SET_SCAN_TIME = 0x25
    SET_BAUD_RATE = 0x28
    SET_POWER = 0x2F
    ACOUSTO_OPTIC_CONTROL = 0x33


class STATUS:
    INVENTORY_OK = 0x01
    INVENTORY_TIMEOUT = 0x02
    INVENTORY_MORE_DATA = 0x03
    INVENTORY_FLASH_FULL = 0x04
    ERROR_COMMAND_EXECUTE = 0xF9
    ERROR_POOR_COMMS = 0xFA
    ERROR_NO_TAG = 0xFB
    ERROR_TAG_INTERNAL = 0xFC
    ERROR_COMMAND_LENGTH = 0xFD
    ERROR_ILLEGAL_COMMAND = 0xFE
    ERROR_PARAMETER = 0xFF


TYPES = {"ru5102": 0x08, "rru2881": 0x0C}


REGIONS = {
    "user": {"code": 0b0000, "base": 902.6, "step": 0.4},
    "china2": {"code": 0b0001, "base": 920.125, "step": 0.25},
    "usa": {"code": 0b0010, "base": 902.75, "step": 0.5, "max_n": 49},
    "korea": {"code": 0b0011, "base": 917.1, "step": 0.2},
    "eu": {"code": 0b0100, "base": 865.1, "step": 0.2},
    "ukraine": {"code": 0b0110, "base": 868.0, "step": 0.1},
    "peru": {"code": 0b0111, "base": 916.2, "step": 0.9},
    "china1": {"code": 0b1000, "base": 840.125, "step": 0.25},
}
