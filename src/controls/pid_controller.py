from components.enums import dwell_state
from src.components.pots.pot import Pot
from components.algorithms.pid_algorithm import PidContoller
from src.services.db.db_pid_values import DbPidValues


class PidController:
    def __init__(self, pot: Pot):
        self.pot = pot
        self.pid = PidContoller(*DbPidValues.get_pid_values(self.pot.pot_type)) # * = unpacking-operator

    def tick(self):
        if not dwell_state.heating(dwell_state):
            self.pot.heat_val = 0.0
            return []
        
        self.pot.heat_val, _ = self.pid.calculate(self.pot.temp_tar, self.pot.temp_now)

        return []