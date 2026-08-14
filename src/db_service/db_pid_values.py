from src.components.models.pid_value import PidValue
from src.components.enums.pot_type import PotType

class PidValueService:

    # PidValue(pot, kp, ki, kd)
    dt = 0.5
    pid_values: dict[PotType: PidValue] = {
        PotType.MASH: PidValue(0.5, 1.5, 0.0),
        PotType.FILL: PidValue(5.0, 0.1, 0.0),
        PotType.COOK: PidValue(0.5, 1.5, 0.0),

        # Previously in PidContoller: dt=0.1, kp=0.1, ki=0.01, kd=0.5
        # Also in Pot: kp=2.9, ki=0.3
        # All values changed, bcs dt was 0.1 but it is the interval and should be 0.5 or 1.0
    }

    @classmethod
    def get_pid_values(cls, pot: PotType):
        return cls.pid_values[pot].get_values()