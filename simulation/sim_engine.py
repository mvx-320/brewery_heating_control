import logging

from simulation.components.thermal_system import ThermalSystem
from src.components.pots.pots import Pot

class SimEngine:
    '''
    Orchistrates ThermalSystems
    Holds simulated time and enables time jumps
    '''

    def __init__(self, mash: Pot, fill: Pot, cook: Pot):
        self.logger = logging.getLogger(__name__)

        self.thermal_systems: dict[Pot: ThermalSystem] = {
            mash: ThermalSystem(mash.pot_type),
            fill: ThermalSystem(fill.pot_type),
            cook: ThermalSystem(cook.pot_type),
        }
        self.time_s = 0.0

        self._sync_pots_from_systems()

    def _power_w(self, pot, system) -> float:
        return pot.heat_val * system.POT_CONFIG.heater_max_power_w

    def _sync_pots_from_systems(self):
        for pot, system in self.thermal_systems.items():
            pot.temp_now = system.state.measured_temperature_c

    def step_seconds(self, n_seconds: int = 1):
        for _ in range(n_seconds):
            for pot, system in self.thermal_systems.items():
                system.step(self._power_w(pot, system))
            self.time_s += 1.0
        self._sync_pots_from_systems()
        return self.time_s

    def advance_to(self, target_s: float):
        if target_s <= self.time_s:
            self.logger.info(f'advance_to: Target {target_s}s is not in the future (currently {self.time_s}s).')
            return self.time_s

        steps = int(round(target_s - self.time_s))
        self.logger.info(f'Time jump: {self.time_s}s -> {target_s}s ({steps}s simulated)')
        self.step_seconds(steps)
        return self.time_s
    
    def reset(self):
        self.time_s = 0.0
        self.thermal_systems = {
            self.mash: ThermalSystem(self.mash.pot_type),
            self.fill: ThermalSystem(self.fill.pot_type),
            self.cook: ThermalSystem(self.cook.pot_type),
        }