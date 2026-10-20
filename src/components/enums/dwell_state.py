from enum import Enum

class DwellState(Enum):
    IDLE = 0
    WAITING = 1
    PENDING = 2
    ALARM = 3
    FINISHED = 4 # Last dwell is finished