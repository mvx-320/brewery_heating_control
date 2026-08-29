from dataclasses import dataclass

@dataclass
class SimPotConfig:
    temperature_fluid_init_c: float
    temperature_ambient_c: float

    fluid_volume_l: int
    fluid_density_kg_per_l: float
    fluid_heat_capacity_j_per_kg_k: int

    pot_diameter_m: float
    pot_height_m: float
    pot_mass_kg: float
    pot_heat_capacity_j_per_kg_k: int

    heater_max_power_w: int
    heater_efficiency: float

    heat_loss_coefficient_w_per_k: float

    evaporation_start_temperature_c: int
    evaporation_loss_at_100c_w: int

    sensor_time_constant_s: int
    sensor_noise_std_c: float


