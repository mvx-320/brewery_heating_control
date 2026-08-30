import sys, logging
sys.path.append("src/components")

from PyQt5.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker

from src.components.enums.pot_type import PotType
from src.db_service.db_pid_values import PidValuesService
from src.components.pid_controller import PidContoller


class Pot(QObject):
    
    temp_now_changed = pyqtSignal(float)
    heat_val_changed = pyqtSignal(float)
    
    def __init__(self, pot_type: PotType, debug_enabled: bool, dt= 0.1, kp= 5, ki= 0.1, kd= 0): # before kp= 2.9, ki= 0.3
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.pot_type = pot_type
        self.temp_now_lock = QMutex()
        self._temp_now = 0.0 # Overriten from serial component and Debug -> temp_now_low
        self._temp_tar = 0.0
        self._heat_val = 0.0 # 0.0 - 1.0
        self.heat_regulation = False
        self.debug_enabled = debug_enabled
        self.pid = PidContoller(*PidValuesService.get_pid_values(self.pot_type)) # * = unpacking-operator

        # Thermal System for the pot is in sim_engine.py. It shouldn't be initialized in the deployed state


    @property
    def temp_now(self):
        return self._temp_now
    
    @temp_now.setter
    def temp_now(self, new_temp: float):
        locker = QMutexLocker(self.temp_now_lock)
        if self._temp_now != new_temp:
            self._temp_now = new_temp
            self.temp_now_changed.emit(new_temp)


    @property
    def temp_tar(self):
        return self._temp_tar
    
    @temp_tar.setter
    def temp_tar(self, new_temp: float):
        if new_temp < 0:
            raise ValueError ("new target value < 0")
        if new_temp > 120:
            raise ValueError ("new target value > 120")
        self.logger.info(f'{self.pot_type.name}.temp_tar = {new_temp}')
        self._temp_tar = new_temp


    @property
    def heat_val(self):
        return self._heat_val
        
    @heat_val.setter
    def heat_val(self, new_temp: int):
        if self._heat_val != new_temp:
            self._heat_val = new_temp
            self.heat_val_changed.emit(new_temp)

