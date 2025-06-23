from PyQt5.QtCore import QObject, QTimer, pyqtSignal
import logging

from pid_controller import myPID
from period_heat_reg import PeriodTimePot


class Pot(QObject):
    
    temp_now_changed = pyqtSignal(float)
    heat_val_changed = pyqtSignal(int)
    
    def __init__(self, name, dt= 0.1, max_w= 3500, min_w= 0, kp= 5, ki= 0.1, kd= 0): # before kp= 2.9, ki= 0.3
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.name = name
        self._temp_now = 0.0
        self._temp_tar = 0.0
        self._heat_val = 0
        self.heat_regulation = False
        self.pid = myPID(dt, max_w, min_w, kp, ki, kd)
        self.logger.info(f"Pot '{name}' initialized")


    @property
    def temp_now(self):
        return self._temp_now
    
    @temp_now.setter
    def temp_now(self, new_temp: float):
        if self._temp_now != new_temp:
            old_temp = self._temp_now
            self._temp_now = new_temp
            self.temp_now_changed.emit(new_temp)
            self.logger.debug(f"{self.name} temperature changed: {old_temp:.1f}°C -> {new_temp:.1f}°C")


    @property
    def temp_tar(self):
        return self._temp_tar
    
    @temp_tar.setter
    def temp_tar(self, new_temp: float):
        if new_temp < 0:
            raise ValueError ("new target value < 0")
        if new_temp > 120:
            raise ValueError ("new target value > 120")
        if self._temp_tar != new_temp:
            old_temp = self._temp_tar
            self._temp_tar = new_temp
            self.logger.info(f"{self.name} target temperature changed: {old_temp:.1f}°C -> {new_temp:.1f}°C")
        print(f'{self.name}.temp_tar = {new_temp}')


    @property
    def heat_val(self):
        return self._heat_val
        
    @heat_val.setter
    def heat_val(self, new_temp: int):
        if self._heat_val != new_temp:
            old_heat = round(self._heat_val)
            self._heat_val = new_temp
            self.heat_val_changed.emit(new_temp)
            if abs(old_heat - new_temp) > 100:  # Only log significant changes
                self.logger.info(f"{self.name} heat value changed: {old_heat}W -> {new_temp}W")


class TimerPot(Pot):
    act_time_changed = pyqtSignal(float)
    run_state_changed = pyqtSignal(int)
    
    def __init__(self, name, interval_s= 0.1, dt= 0.1, max_w= 3500, min_w= 0, kp= 0.5, ki= 1.5, kd= 0): # ki war vorher bei 0.2
        super().__init__(name, dt= dt, max_w= max_w, min_w= min_w, kp= kp, ki= ki, kd= kd)
        self._act_time = 0
        self.logger_time = 0
        
        self.interval_s = interval_s
        self._run_state = 0
        self.logger.info(f"TimerPot '{name}' initialized with interval {interval_s}s")
        
        
    @property
    def act_time(self):
        return self._act_time
    
    @act_time.setter
    def act_time(self, new_time: float):
        if (new_time <0):
            self.run_state = 3
        else:
            pass
            
        self._act_time = new_time
        self.act_time_changed.emit(abs(new_time)) # could be abs() if you don't like neg. numbers
        if abs(new_time - self.logger_time) > 30:  # Only log significant time changes
            self.logger.info(f"{self.name} timer is on: {new_time/60:.1f}min")
            self.logger_time = new_time
        
        
    @property
    def run_state(self):
        return self._run_state
    
    @run_state.setter
    def run_state(self, new_state: int):
        old_state = self._run_state
        self.run_state_changed.emit(new_state)
        self._run_state = new_state
        if old_state != new_state:
            states = ["Stopped", "Running", "Active", "Finished"]
            self.logger.info(f"{self.name} run state changed: {states[old_state]} -> {states[new_state]}")
        #print(f'{self.name}.run_state = {new_state}')
        
        
            
