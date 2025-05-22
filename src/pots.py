
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

from pid_controller import myPID
from period_heat_reg import PeriodTimePot


class Pot(QObject):
    
    temp_now_changed = pyqtSignal(float)
    heat_val_changed = pyqtSignal(int)
    
    def __init__(self, name, dt= 0.1, max_w= 3500, min_w= 0, kp= 5, ki= 0.1, kd= 0): # before kp= 2.9, ki= 0.3
        super().__init__()
        self.name = name
        self._temp_now = 0.0
        self._temp_tar = 0.0
        self._heat_val = 0
        self.heat_regulation = False
        self.pid = myPID(dt, max_w, min_w, kp, ki, kd)


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
        print(f'{self.name}.temp_tar = {new_temp}')
        self._temp_tar = new_temp


    @property
    def heat_val(self):
        return self._heat_val
        
    @heat_val.setter
    def heat_val(self, new_temp: int):
        if self._heat_val != new_temp:
            self._heat_val = new_temp
            self.heat_val_changed.emit(new_temp)


class TimerPot(Pot):
    act_time_changed = pyqtSignal(float)
    run_state_changed = pyqtSignal(int)
    
    def __init__(self, name, interval_s= 0.1, dt= 0.1, max_w= 3500, min_w= 0, kp= 0.5, ki= 1.5, kd= 0): # ki war vorher bei 0.2
        super().__init__(name, dt= dt, max_w= max_w, min_w= min_w, kp= kp, ki= ki, kd= kd)
        self._act_time = 0
        
        self.interval_s = interval_s
        self._run_state = 0
        
        
    @property
    def act_time(self):
        return self._act_time
    
    @act_time.setter
    def act_time(self, new_time: float):
        if (new_time <0):
            #self.time_elapsed = True
            self.run_state = 3
        else:
            #self.time_elapsed = False
            pass
            
        self._act_time = new_time
        self.act_time_changed.emit(abs(new_time))
        
        
    @property
    def run_state(self):
        return self._run_state
    
    @run_state.setter
    def run_state(self, new_state: int):
        self.run_state_changed.emit(new_state)
        self._run_state = new_state
        print(f'{self.name}.run_state = {new_state}')
        
        
            
