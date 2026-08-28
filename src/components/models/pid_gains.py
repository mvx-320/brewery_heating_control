from dataclasses import dataclass

@dataclass
class PidGains:
    kp: float
    ki: float
    kd: float