from dataclasses import dataclass

@dataclass
class SimState:
    fluid_temperature_c: float
    sensor_temperature_c: float
    measured_temperature_c: float
    heater_power_w: float = 0.0