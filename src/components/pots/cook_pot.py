from PyQt5.QtCore import pyqtSignal 
from src.components.pots.pots import Pot
from src.components.enums.pot_type import PotType


class CookPot(Pot):
   rest_time_ds_changed = pyqtSignal(int)
   run_state_changed = pyqtSignal(int)

    
   def __init__(self, pot_type: PotType):
       super().__init__(pot_type)
       self._rest_time_ds: int = 0
        
       self._run_state = 0
        
        
   @property
   def rest_time_ds(self):
       return self._rest_time_ds
    
   @rest_time_ds.setter
   def rest_time_ds(self, new_time: int):
       if new_time < 0:
           self.run_state = 3
           new_time = 0
               
       self._rest_time_ds = new_time
       self.rest_time_ds_changed.emit(new_time)
        
        
   @property
   def run_state(self):
       return self._run_state
    
   @run_state.setter
   def run_state(self, new_state: int):
       self.run_state_changed.emit(new_state)
       self._run_state = new_state
       self.logger.info(f'{self.pot_type.name}.run_state = {new_state}')
        
        
            