from src.components.enums.pot_type import PotType
from src.components.models.pid_gains import PidGains
from src.components.models.pid_cool_factor import PidCoolFactor

class PidValuesService:

    dt = 1

    pid_gains: dict[PotType: dict[int, PidGains]] = {
        PotType.MASH: {
            30: PidGains(
                kp=0.1, 
                ki=0.000047, 
                kd=0.04,
            ),
            80: PidGains(
                kp=0.1, 
                ki=0.00016, 
                kd=0.04,
            ),
        },
        PotType.FILL: {
            30: PidGains(
                kp=0.1, 
                ki=0.000047, 
                kd=0.04,
            ),
            80: PidGains(
                kp=0.1, 
                ki=0.00016, 
                kd=0.04,
            ),
        },
        PotType.COOK: {
            30: PidGains(
                kp=0.1, 
                ki=0.000047, 
                kd=0.04,
            ),
            80: PidGains(
                kp=0.1, 
                ki=0.00016, 
                kd=0.04,
            ),
        },
        # Previously in PidContoller: dt=0.1, kp=0.1, ki=0.01, kd=0.5
        # Also in Pot: kp=2.9, ki=0.3
        # All values changed, bcs dt was 0.1 but it is the interval and should be 0.5 or 1.0
    }

    pid_cool_factors = PidCoolFactor(
        threshold=-2.0, # error < (set - act)
        factor30=6.00,
        factor50=1.40,
        factor80=0.01,
    )

    pid_tm_labs: dict[PotType: float] = {
        PotType.MASH: 5.0,
        PotType.FILL: 5.0,
        PotType.COOK: 5.0,
    }

    @classmethod
    def get_pid_values(cls, pot: PotType):
        return \
            cls.dt, \
            cls.pid_gains[pot][30], \
            cls.pid_gains[pot][80], \
            cls.pid_cool_factors, \
            cls.pid_tm_labs[pot]