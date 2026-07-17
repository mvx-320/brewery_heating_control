from PyQt5.QtCore import pyqtSignal 
from components.pots.pots import Pot


class CookPot(Pot):
   rest_time_changed = pyqtSignal(int)
   run_state_changed = pyqtSignal(int)

    
   def __init__(self, name, interval_ds= 1, dt= 0.1, max_w= 3500, min_w= 0, kp= 0.5, ki= 1.5, kd= 0): # ki war vorher bei 0.2
       super().__init__(name, dt= dt, max_w= max_w, min_w= min_w, kp= kp, ki= ki, kd= kd)
       self._rest_time: int = 0
        
       self.interval_ds = interval_ds  # Dezisekunden (1 ds = 100ms)
       self._run_state = 0
        
        
   @property
   def rest_time(self):
       return self._rest_time
    
   @rest_time.setter
   def rest_time(self, new_time: int):
       if new_time < 0:
           self.run_state = 3
           new_time = 0
               
       self._rest_time = new_time
       self.rest_time_changed.emit(new_time)
        
        
   @property
   def run_state(self):
       return self._run_state
    
   @run_state.setter
   def run_state(self, new_state: int):
       self.run_state_changed.emit(new_state)
       self._run_state = new_state
       self.logger.info(f'{self.name}.run_state = {new_state}')
        
        
            