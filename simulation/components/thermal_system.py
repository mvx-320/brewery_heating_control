import random
from src.components.enums.pot_type import PotType
from src.db_service.db_sim_config import SimConfigService
from src.db_service.db_pid_values import PidValuesService
from simulation.components.models.sim_state import SimState

class ThermalSystem:
    def __init__(self, pot: PotType, seed=42):
        self.POT_CONFIG = SimConfigService.pot_sim_config[pot]

        self.rng = random.Random(seed)

        self.fluid_mass_kg = self.POT_CONFIG.fluid_volume_l * self.POT_CONFIG.fluid_density_kg_per_l

        self.fluid_heat_capacity_j_per_k = self.fluid_mass_kg * self.POT_CONFIG.fluid_heat_capacity_j_per_kg_k
        self.pot_heat_capacity_j_per_k = self.POT_CONFIG.pot_mass_kg * self.POT_CONFIG.pot_heat_capacity_j_per_kg_k
        self.total_heat_capacity_j_per_k = self.fluid_heat_capacity_j_per_k + self.pot_heat_capacity_j_per_k

        self.state = SimState(
            fluid_temperature_c=self.POT_CONFIG.temperature_fluid_init_c,
            sensor_temperature_c=self.POT_CONFIG.temperature_fluid_init_c,
            measured_temperature_c=self.POT_CONFIG.temperature_fluid_init_c,
        )


    def calculate_heat_loss(self, temperature_c):
        # Heat loss increases with the temperature difference to ambient.
        temperature_difference = max(0.0, temperature_c - self.POT_CONFIG.temperature_fluid_init_c)
        heat_loss_w = self.POT_CONFIG.heat_loss_coefficient_w_per_k * temperature_difference

        # The lid reduces evaporation, but evaporation still matters at high temperatures.
        if temperature_c > self.POT_CONFIG.evaporation_start_temperature_c:
            normalized_temperature = (temperature_c - self.POT_CONFIG.evaporation_start_temperature_c) / \
                (100.0 - self.POT_CONFIG.evaporation_start_temperature_c)

            normalized_temperature = max(0.0, min(normalized_temperature, 1.0))

            heat_loss_w += (self.POT_CONFIG.evaporation_loss_at_100c_w * normalized_temperature**2)

        return heat_loss_w

    def step(self, heater_power_w):
        # Clamp the requested power to the physical heater range.
        heater_power_w = max(0.0, min(heater_power_w, self.POT_CONFIG.heater_max_power_w))
        delivered_power_w = heater_power_w * self.POT_CONFIG.heater_efficiency

        heat_loss_w = self.calculate_heat_loss(self.state.fluid_temperature_c)
        net_power_w = delivered_power_w - heat_loss_w

        temperature_change_c = net_power_w * PidValuesService.dt / self.total_heat_capacity_j_per_k

        self.state.fluid_temperature_c += temperature_change_c
        self.state.heater_power_w = heater_power_w

        # Model the pysical sensor as a first-order response.
        sensor_alpha = min(1.0, PidValuesService.dt / self.POT_CONFIG.sensor_time_constant_s)

        self.state.sensor_temperature_c += sensor_alpha * (self.state.fluid_temperature_c - self.state.sensor_temperature_c)

        # Add measurement noise after the sensor response.
        self.state.measured_temperature_c = self.state.sensor_temperature_c + self.rng.gauss(0.0, self.POT_CONFIG.sensor_noise_std_c)

        return self.state