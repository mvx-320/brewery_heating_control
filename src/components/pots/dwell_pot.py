import sys, logging
sys.path.append("src")

from PyQt5.QtCore import QObject, QMutex, QMutexLocker, pyqtSignal

from src.gui.dwell_frame import Dwell
from components.pots.pot import Pot
from src.components.enums.pot_type import PotType

class DwellPot(Pot):
    dwell_array_mutex = QMutex() # TODO: Maybe use lock() and unlock() if QMutexLocker is not working.
    _current_dwell_index: int = -1
    rest_time_ds_changed = pyqtSignal(int)
    run_state_changed = pyqtSignal(int)
    current_dwell_index_changed = pyqtSignal(int)
    dwell_progress_changed = pyqtSignal(int, int, int, int)  # dwell_index, elapsed_ds, total_ds, remaining_ds
    dwell_finished = pyqtSignal()
    tar_temp_changed = pyqtSignal(float)
    
    def __init__(self, pot_type: PotType): 
       super().__init__(pot_type)
    #    self._rest_time_ds: int = 0
        
    #    self._run_state = 0
        
    # region getter, setter
    @property
    def current_dwell_index(self):
        return self._current_dwell_index
    
    @current_dwell_index.setter
    def current_dwell_index(self, new_index: int):
        self._current_dwell_index = new_index
        self.current_dwell_index_changed.emit(new_index)
        
    # @property
    # def rest_time_ds(self):
    #     return self._rest_time_ds
        
    # @rest_time_ds.setter
    # def rest_time_ds(self, new_time: int):
    #     if new_time < 0:
    #         self.run_state = 3
    #         new_time = 0
                
    #     self._rest_time_ds = new_time
    #     self.rest_time_ds_changed.emit(new_time)
            
    # SIMULATION ONLY TODO: Move to DwellController later
    def set_rest_time_ds_percentage(self, percentage: float):
        if not self.simulation_enabled: return # TODO: simulation_enabled is not a thing

        locker = QMutexLocker(self.dwell_array_mutex)
        total_time_ds = self._dwell_array[self._current_dwell_index].tar_time_ds
        locker.unlock()

        new_rest_time_ds = int(total_time_ds * (1 - percentage / 100))
        self.rest_time_ds = new_rest_time_ds

            
    # @property
    # def run_state(self):
    #     return self._run_state
        
    # @run_state.setter
    # def run_state(self, new_state: int):
    #     self.run_state_changed.emit(new_state)
    #     self._run_state = new_state
    #     self.logger.info(f'{self.pot_type.name}.run_state = {new_state}')

    # TODO: Add getter, setter für dwell_array
    
    # region dwell_array
    # def get_dwell_array(self) -> list[Dwell]:
    #     locker = QMutexLocker(self.dwell_array_mutex)
    #     return self._dwell_array


    # region runtime environment
    # def next_dwell(self):
    #     locker = QMutexLocker(self.dwell_array_mutex)
    #     if self._current_dwell_index < len(self._dwell_array) -1:
    #         self.current_dwell_index = self._current_dwell_index + 1
    #         self.logger.info(f'{self.pot_type.name} switched to dwell {self._current_dwell_index}')
    #     else:
    #         # TODO: Change Pause button to Stop button
    #         self.logger.info(f'{self.pot_type.name} reached end of dwell array') 