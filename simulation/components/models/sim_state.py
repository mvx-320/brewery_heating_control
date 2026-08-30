from dataclasses import dataclass

@dataclass
class SimState:
    fluid_temperature_c: float
    sensor_temperature_c: float
    measured_temperature_c: float
    heater_power_w: float = 0.0

    def override(self, temperature_c: float):
        self.fluid_temperature_c = temperature_c
        self.sensor_temperature_c = temperature_c
        self.measured_temperature_c = temperature_c