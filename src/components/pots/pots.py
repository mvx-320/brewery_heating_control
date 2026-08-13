import sys, logging
sys.path.append("src/components")

from PyQt5.QtCore import QObject, pyqtSignal

from pid_controller import myPID


class Pot(QObject):
    
    temp_now_changed = pyqtSignal(float)
    heat_val_changed = pyqtSignal(float)
    
    def __init__(self, name, debug_enabled, dt= 0.1, kp= 5, ki= 0.1, kd= 0): # before kp= 2.9, ki= 0.3
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.name = name
        self._temp_now = 0.0
        self._temp_tar = 0.0
        self._heat_val = 0.0 # 0.0 - 1.0
        self.heat_regulation = False
        self.debug_enabled = debug_enabled
        self.pid = myPID(dt, kp, ki, kd) # TODO: Safe persitant in DB later, maybe even make it adjustable in the UI


    @property
    def temp_now(self):
        return self._temp_now
    
    @temp_now.setter
    def temp_now(self, new_temp: float):
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
        self.logger.info(f'{self.name}.temp_tar = {new_temp}')
        self._temp_tar = new_temp


    @property
    def heat_val(self):
        return self._heat_val
        
    @heat_val.setter
    def heat_val(self, new_temp: int):
        if self._heat_val != new_temp:
            self._heat_val = new_temp
            self.heat_val_changed.emit(new_temp)

