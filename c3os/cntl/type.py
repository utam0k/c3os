from enum import IntEnum


class CNTLTYPE(IntEnum):
    """CNTL type enum

    Attributes:
        CREATE_INSTANCE(int): Create instance.
        DELETE_INSTANCE(int): Delete instance.
    """

    CREATE_INSTANCE = 0
    DELETE_INSTANCE = 1
