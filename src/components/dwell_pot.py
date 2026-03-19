import sys, logging
sys.path.append("src/components")

from PyQt5.QtCore import QObject, pyqtSignal

from pid_controller import myPID
import dwell_frame

class DwellPot(Pot):
    _dwell_array: list[dwell_frame.Dwell] = [
        dwell_frame.Dwell(50.0, None, True),
        dwell_frame.Dwell(60.0, 20.0, False),
        dwell_frame.Dwell(60.0, 20.0, False),
        dwell_frame.Dwell(60.0, 20.0, False),
        dwell_frame.Dwell(60.0, 20.0, False),
        dwell_frame.Dwell(60.0, None, False),
    ]
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
        self.logger.info(f'{self.name}.run_state = {new_state}')

    # TODO: Add getter, setter für dwell_array
            
            
                



