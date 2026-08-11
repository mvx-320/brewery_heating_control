import sys, logging
sys.path.append("src")

from PyQt5.QtCore import QObject, QMutex, QMutexLocker, pyqtSignal

from components.pid_controller import myPID
from gui.dwell_frame import Dwell
from pots.pots import Pot

class DwellPot(Pot):
    dwell_array_mutex = QMutex() # TODO: Maybe use lock() and unlock() if QMutexLocker is not working.
    _dwell_array: list[Dwell] = [ # TODO: Eventuell komplett in eine lokale Datenbank verschieben
        Dwell(30.0, None, True),    # Einmaischen: keine Zeit, nur Temperatur
        Dwell(30.0, 12000, False),  # 20 min = 12000 ds
        Dwell(40.0, 12000, False),
        Dwell(60.0, 12000, True),
        Dwell(60.0, 12000, False),
        Dwell(60.0, None, False),   # Ausmaischen: keine Zeit
    ]

    _current_dwell_index: int = -1
    rest_time_changed = pyqtSignal(int)
    run_state_changed = pyqtSignal(int)
    current_dwell_index_changed = pyqtSignal(int)
    dwell_progress_changed = pyqtSignal(int, int, int, int)  # dwell_index, elapsed_ds, total_ds, remaining_ds
    dwell_finished = pyqtSignal()
    tar_temp_changed = pyqtSignal(float)
    
    def __init__(self, name, interval_ds= 1, dt= 0.1, max_w= 3500, min_w= 0, kp= 0.5, ki= 1.5, kd= 0): # ki war vorher bei 0.2
       super().__init__(name, dt= dt, max_w= max_w, min_w= min_w, kp= kp, ki= ki, kd= kd)
       self._rest_time: int = 0
        
       self.interval_ds = interval_ds  # Dezisekunden (1 ds = 100ms)
       self._run_state = 0
        
    # region getter, setter
    @property
    def current_dwell_index(self):
        return self._current_dwell_index
    
    @current_dwell_index.setter
    def current_dwell_index(self, new_index: int):
        self._current_dwell_index = new_index
        self.current_dwell_index_changed.emit(new_index)
        
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

    # TODO: Add getter, setter für dwell_array
    @property
    def tar_temp(self):
        locker = QMutexLocker(self.dwell_array_mutex) # All these lockers should prevent race conditions on dwell_array.
        return self._dwell_array[self._current_dwell_index].tar_temp

    @tar_temp.setter
    def tar_temp(self, new_temp: float):
        if new_temp < 0:
            raise ValueError ("new target value < 0")
        if new_temp > 120:
            raise ValueError ("new target value > 120")

        locker = QMutexLocker(self.dwell_array_mutex)
        self._dwell_array[self._current_dwell_index].tar_temp = new_temp
        self.tar_temp_changed.emit(new_temp)
        self.logger.info(f'dwell_array[{self._current_dwell_index}].tar_temp = {new_temp}')

    @property
    def tar_time_ds(self):
        locker = QMutexLocker(self.dwell_array_mutex)
        return self._dwell_array[self._current_dwell_index].tar_time_ds
    
    @tar_time_ds.setter
    def tar_time_ds(self, new_time: int):
        if new_time < 0:
            raise ValueError ("new target value < 0")

        locker = QMutexLocker(self.dwell_array_mutex)
        self._dwell_array[self._current_dwell_index].tar_time_ds = new_time
        self.logger.info(f'dwell_array[{self._current_dwell_index}].tar_time_ds = {new_time}')
    
    # region dwell_array
    def get_dwell_array(self) -> list[Dwell]:
        locker = QMutexLocker(self.dwell_array_mutex)
        return self._dwell_array

    def dwell_up(self, obj) -> list[Dwell]:
        locker = QMutexLocker(self.dwell_array_mutex)
        index = next(i for i, x in enumerate(self._dwell_array) if x is obj)
        if index > 1:
            del self._dwell_array[index]
            self._dwell_array.insert(index -1, obj)
        return self._dwell_array

    def dwell_down(self, obj) -> list[Dwell]:
        locker = QMutexLocker(self.dwell_array_mutex)
        index = next(i for i, x in enumerate(self._dwell_array) if x is obj)
        if index < len(self._dwell_array) -2:
            del self._dwell_array[index]
            self._dwell_array.insert(index +1, obj)
        return self._dwell_array

    def dwell_new(self, obj) -> list[Dwell]:
        locker = QMutexLocker(self.dwell_array_mutex)
        index = next(i for i, x in enumerate(self._dwell_array) if x is obj)
        self._dwell_array.insert(index +1, Dwell(None, None, False))
        return self._dwell_array

    def dwell_delete(self, obj) -> list[Dwell]:
        locker = QMutexLocker(self.dwell_array_mutex)
        index = next(i for i, x in enumerate(self._dwell_array) if x is obj)
        if (len(self._dwell_array) <= 2):
            print("Error: There can not be less than 2 dwells")
            map(lambda d: d.makeBound(), self._dwell_array)
            return
        del self._dwell_array[index]
        return self._dwell_array

    # region runtime environment
    def next_dwell(self):
        locker = QMutexLocker(self.dwell_array_mutex)
        if self._current_dwell_index < len(self._dwell_array) -1:
            self.current_dwell_index = self._current_dwell_index + 1
            self.logger.info(f'{self.name} switched to dwell {self._current_dwell_index}')
        else:
            # TODO: Change Pause button to Stop button
            self.logger.info(f'{self.name} reached end of dwell array') 