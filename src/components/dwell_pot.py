import sys, logging
sys.path.append("src")

from PyQt5.QtCore import QObject, QMutex, QMutexLocker, pyqtSignal

from components.pid_controller import myPID
from gui import dwell_frame
from components.pots import Pot

class DwellPot(Pot):
    dwell_array_mutex = QMutex() # TODO: Maybe use lock() and unlock() if QMutexLocker is not working.
    _dwell_array: list[dwell_frame.Dwell] = [ # TODO: Eventuell komplett in eine lokale Datenbank verschieben
        dwell_frame.Dwell(50.0, None, True),  # TODO: Wahrscheinlich wird hier Dwell über dwell_frame importiert. Das macht vllt keinen Sinn. zirkuläre Abhängigkeit.
        dwell_frame.Dwell(60.0, 20.0, False),
        dwell_frame.Dwell(60.0, 20.0, False),
        dwell_frame.Dwell(60.0, 20.0, True),
        dwell_frame.Dwell(60.0, 20.0, False),
        dwell_frame.Dwell(60.0, None, False),
    ]

    _current_dwell_index: int = 0
    act_time_changed = pyqtSignal(float)
    run_state_changed = pyqtSignal(int)
    
    def __init__(self, name, interval_s= 0.1, dt= 0.1, max_w= 3500, min_w= 0, kp= 0.5, ki= 1.5, kd= 0): # ki war vorher bei 0.2
       super().__init__(name, dt= dt, max_w= max_w, min_w= min_w, kp= kp, ki= ki, kd= kd)
       self._act_time = 0
        
       self.interval_s = interval_s
       self._run_state = 0
        
    # region getter, setter
        
    @property
    def act_time(self):
        return self._act_time
        
    @act_time.setter
    def act_time(self, new_time: float): # TODO: Maybe run_state is not usefull anymore. Maybe the logic can be removed here and be done in the Runtime Environment
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
        self.logger.info(f'dwell_array[{self._current_dwell_index}].tar_temp = {new_temp}')

    @property
    def tar_time(self):
        locker = QMutexLocker(self.dwell_array_mutex)
        return self._dwell_array[self._current_dwell_index].tar_time
    
    @tar_time.setter
    def tar_time(self, new_time: float):
        if new_time < 0:
            raise ValueError ("new target value < 0")

        locker = QMutexLocker(self.dwell_array_mutex)
        self._dwell_array[self._current_dwell_index].tar_time = new_time
        self.logger.info(f'dwell_array[{self._current_dwell_index}].tar_time = {new_time}')
    
    # region dwell_array
    def get_dwell_array(self) -> list[dwell_frame.Dwell]:
        locker = QMutexLocker(self.dwell_array_mutex)
        return self._dwell_array

    def dwell_up(self, obj) -> list[dwell_frame.Dwell]:
        locker = QMutexLocker(self.dwell_array_mutex)
        index = next(i for i, x in enumerate(self._dwell_array) if x is obj)
        if index > 1:
            del self._dwell_array[index]
            self._dwell_array.insert(index -1, obj)
        return self._dwell_array

    def dwell_down(self, obj) -> list[dwell_frame.Dwell]:
        locker = QMutexLocker(self.dwell_array_mutex)
        index = next(i for i, x in enumerate(self._dwell_array) if x is obj)
        if index < len(self._dwell_array) -2:
            del self._dwell_array[index]
            self._dwell_array.insert(index +1, obj)
        return self._dwell_array

    def dwell_new(self, obj) -> list[dwell_frame.Dwell]:
        locker = QMutexLocker(self.dwell_array_mutex)
        index = next(i for i, x in enumerate(self._dwell_array) if x is obj)
        self._dwell_array.insert(index +1, dwell_frame.Dwell(None, None, False))
        return self._dwell_array

    def dwell_delete(self, obj) -> list[dwell_frame.Dwell]:
        locker = QMutexLocker(self.dwell_array_mutex)
        index = next(i for i, x in enumerate(self._dwell_array) if x is obj)
        if (len(self._dwell_array) <= 2):
            print("Error: There can not be less than 2 dwells")
            map(lambda d: d.makeBound(), self._dwell_array)
            return
        del self._dwell_array[index]
        return self._dwell_array