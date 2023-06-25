from abc import ABC
from enum import Enum


class OperatorTypes(Enum):
    MASTER = "master"
    WORKER = "worker"


class OperatorDaemon(ABC):
    def __init__(self, operator_type: OperatorTypes):
        self.operator_type = operator_type
