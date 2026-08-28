from dataclasses import dataclass

@dataclass
class PidCoolFactor:
    threshold: float
    factor30: float
    factor50: float
    factor80: float