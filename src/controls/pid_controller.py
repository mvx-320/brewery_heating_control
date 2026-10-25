from src.components.enums import dwell_state
from src.components.enums.pot_type import PotType
from src.components.algorithms.pid_algorithm import PidAlgorithm
from src.dtos.dwell_events import HeatValChangedEvent
from src.services.db.db_pid_values import DbPidValues


class PidController:
    def __init__(self, pot_type: PotType):
        self._pot_type = pot_type
        self._pid = PidAlgorithm(*DbPidValues.get_pid_values(self._pot_type)) # * = unpacking-operator

        self._enabled = False

    def tick(self, temp_tar : float, temp_now : float) -> list: 

        heat_val = self._pid.calculate(temp_tar, temp_now)

        return [HeatValChangedEvent(heat_val)]
