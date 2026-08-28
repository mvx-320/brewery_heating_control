from src.components.enums.pot_type import PotType
from mockups.models.pot_sim_config import PotSimConfig

class SimConfigService:
    pot_sim_config: dict[PotType: PotSimConfig] = {
        PotType.MASH: PotSimConfig(
            temperature_fluid_init_c=20.0,
            temperature_ambient_c=20.0,
            
            fluid_volume_l=100,
            fluid_density_kg_per_l=1.067,
            # Google AI said 3600-3900J/(kg*K)
            # But I saw 1670J/(kg*K) on a forum
            fluid_heat_capacity_j_per_kg_k=1670,
        
            pot_diameter_m=0.5,
            pot_height_m=0.55,
            pot_mass_kg=12.0,
            pot_heat_capacity_j_per_kg_k=500,

            heater_max_power_w=3500,
            heater_efficiency=.98,

            heat_loss_coefficient_w_per_k=34.0,

            evaporation_start_temperature_c=60,
            evaporation_loss_at_100c_w=350,

            sensor_time_constant_s=2*60,
            sensor_noise_std_c=0.01,
        ),

        PotType.FILL: PotSimConfig(
            temperature_fluid_init_c=20.0,
            temperature_ambient_c=20.0,
            
            fluid_volume_l=100,
            fluid_density_kg_per_l=1.067,
            # Water has 4186J/(kg*K)
            fluid_heat_capacity_j_per_kg_k=4186,
        
            pot_diameter_m=0.5,
            pot_height_m=0.55,
            pot_mass_kg=12.0,
            pot_heat_capacity_j_per_kg_k=500,

            heater_max_power_w=3500,
            heater_efficiency=.98,

            heat_loss_coefficient_w_per_k=34.0,

            evaporation_start_temperature_c=60,
            evaporation_loss_at_100c_w=350,

            sensor_time_constant_s=2*60,
            sensor_noise_std_c=0.01,
        ),
    
        PotType.COOK: PotSimConfig(
            temperature_fluid_init_c=20.0,
            temperature_ambient_c=20.0,
            
            fluid_volume_l=120,
            fluid_density_kg_per_l=1.067,
            # Water has 4186J/(kg*K)
            fluid_heat_capacity_j_per_kg_k=4186,
        
            pot_diameter_m=0.6,
            pot_height_m=0.55,
            pot_mass_kg=12.0,
            pot_heat_capacity_j_per_kg_k=500,

            heater_max_power_w=2*3500,
            heater_efficiency=.98,

            heat_loss_coefficient_w_per_k=34.0,

            evaporation_start_temperature_c=60,
            evaporation_loss_at_100c_w=350,

            sensor_time_constant_s=2*60,
            sensor_noise_std_c=0.01,
        ),
    }