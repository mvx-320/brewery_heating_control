from components.enums import dwell_state
from src.components.enums.pot_type import PotType
from components.algorithms.pid_algorithm import PidContoller
from src.services.db.db_pid_values import DbPidValues
from src.dtos.dwell_events import HeatValChangedEvent


class PidController:
    def __init__(self, pot_type: PotType):
        self._pot_type = pot_type
        self._pid = PidContoller(*DbPidValues.get_pid_values(self.pot_type)) # * = unpacking-operator

    def tick(self, temp_tar : float, temp_now : float) -> list: 
        heat_val = 0.0

        if dwell_state.heating(dwell_state):
            heat_val = self.pid.calculate(temp_tar, temp_now)

        return [HeatValChangedEvent(heat_val)]