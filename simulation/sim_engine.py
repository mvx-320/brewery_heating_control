import logging
from PyQt5.QtCore import QObject, QMutex, QMutexLocker, pyqtSignal

from simulation.components.thermal_system import ThermalSystem
from src.components.enums.pot_type import PotType
from src.components.pots.pots import Pot

class SimEngine(QObject):
    '''
    Orchistrates ThermalSystems
    Holds simulated time and enables time jumps
    '''
    time_s_changed = pyqtSignal(float)

    def __init__(self, mash: Pot, fill: Pot, cook: Pot):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.pots: dict[PotType: Pot] = {
            PotType.MASH: mash,
            PotType.FILL: fill,
            PotType.COOK: cook,
        }

        self.thermal_systems_lock = QMutex()
        self.thermal_systems: dict[PotType: ThermalSystem] = {
            PotType.MASH: ThermalSystem(mash.pot_type),
            PotType.FILL: ThermalSystem(fill.pot_type),
            PotType.COOK: ThermalSystem(cook.pot_type),
        }
        
        self.time_s_lock = QMutex()
        self._time_s = 0.0

        self._sync_pots_from_systems()

    @property
    def time_s(self):
        return self._time_s

    @time_s.setter
    def time_s(self, value: float):
        time_s_locker = QMutexLocker(self.time_s_lock)
        self._time_s = value
        self.time_s_changed.emit(value)

    def _power_w(self, pot_type: PotType, system: ThermalSystem) -> float:
        return self.pots[pot_type].heat_val * system.POT_CONFIG.heater_max_power_w

    def _sync_pots_from_systems(self):
        thermal_systems_locker = QMutexLocker(self.thermal_systems_lock)
        for pot_type, system in self.thermal_systems.items():
            self.pots[pot_type].temp_now = system.state.measured_temperature_c

    def step_seconds(self, n_seconds: int = 1):
        for _ in range(n_seconds):
            thermal_systems_locker = QMutexLocker(self.thermal_systems_lock)
            for pot_type, system in self.thermal_systems.items():
                system.step(self._power_w(pot_type, system))
            thermal_systems_locker.unlock()
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

    def forward(self, delta_s: float):
        if delta_s <= 0:
            return self.time_s
        return self.step_seconds(int(round(delta_s)))
    
    def reset(self):
        self.time_s = 0.0
        thermal_systems_locker = QMutexLocker(self.thermal_systems_lock)
        self.thermal_systems = {
            PotType.MASH: ThermalSystem(self.mash.pot_type),
            PotType.FILL: ThermalSystem(self.fill.pot_type),
            PotType.COOK: ThermalSystem(self.cook.pot_type),
        }