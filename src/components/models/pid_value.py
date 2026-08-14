from src.components.enums.pot_type import PotType

class PidValue:
    def __init__(self, kp:float, ki:float, kd:float):
        self.kp = kp
        self.ki = ki
        self.kd = kd

    def get_values(self):
        return self.kp, self.ki, self.kd