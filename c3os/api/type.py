from enum import IntEnum


class APITYPE(IntEnum):
    """API type enum

    Attributes:
        ADD_DB (int): Add instances infomation.
        CREATE_INSTANCE(int): Create instance.
        DELETE_INSTANCE(int): Delete instance.
    """

    ADD_DB = 0
    CREATE_INSTANCE = 1
    DELETE_INSTANCE = 2
