from enum import Enum


class JobType(Enum):
    UNDEFINED = 0
    OPERATION = 1
    STATUS = 2
    REGISTER = 3
    SHUTDOWN = 4
    RENDER = 5
    NEW_OPERATION = 6
