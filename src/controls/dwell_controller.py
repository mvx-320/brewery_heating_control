from typing import Literal

from src.components.enums.dwell_state import DwellState
from src.components.enums.pot_type import PotType
from src.components.models.dwell import Dwell
from src.controls.pid_controller import PidController
from src.dtos.dwell_events import \
    DwellArrayChangedEvent, \
    DwellProgressChangedEvent, \
    AlarmTriggeredEvent, \
    DwellAdvancedEvent, \
    AllDwellsFinishedEvent
from src.services.db.db_dwells import DbDwells


class DwellController:
    '''
    Controller is not a QObject, no relations to Qt (signals, slots, ...).
    No event loop just the logic methods to control the dwells.
    '''

    def __init__(self, pot_type : PotType):
        # TODO: Maybe add Logger here
        self._pot_type = pot_type
        self._pid_controller = PidController(self._pot_type) 

        self._dwell_state = DwellState.IDLE
        self._current_dwell_index = -1
        self._rest_time_s = 0

        # DB
        self._dwell_array = DbDwells.dwell_array


    #region API
    def start_mash(self) -> list:
        if self._dwell_state in [DwellState.IDLE]:
            return self._to_waiting_state()
        return []

    def stop_mash(self) -> list:
        pass # TODO: Implement stop_mash logic. Add to DwellStateGraph

    def confirm_alarm(self) -> list:
        events = []
        if self._dwell_state in [DwellState.ALARM]:
            next_state = self._state_after_alarm()
            match next_state: # TODO: Move the match to a seperate methode that is called with next_state
                case DwellState.WAITING:
                    events += self._to_waiting_state()
                case DwellState.FINISHED:
                    events += self._to_finished_state()
        return events
    #endregion API
    

    def tick(self, temp_now: float) -> list: 
        '''
        Execute 1/s
        '''
        events = []
        events += self.pid_controller.tick(self._dwell_array[self._current_dwell_index].tar_temp, temp_now)

        match self._dwell_state:
            case DwellState.IDLE:
                return events

            case DwellState.WAITING:
                if self._temp_in_tolerance(temp_now):
                    next_state = self._state_after_waiting()
                    match next_state:
                        case DwellState.PENDING:
                            events += self._to_pending_state()
                return events

            case DwellState.PENDING:
                self.rest_time_s -= 1
                events.append(DwellProgressChangedEvent(
                    dwell_index = self._current_dwell_index,
                    rest_time_s = self.rest_time_s,
                    total_time_s = self._dwell_array[self._current_dwell_index].tar_time_s
                ))

                # Transition
                if self.rest_time_s <= 0:
                    next_state = self._state_after_pending()
                    match next_state:
                        case DwellState.WAITING:
                            events += self._to_waiting_state()
                        case DwellState.ALARM:
                            events += self._to_alarm_state()
                        case DwellState.FINISHED:
                            events += self._to_finished_state()
                return events

            case DwellState.ALARM:
                return events


    def _temp_in_tolerance(self, temp_now: float) -> bool:
        '''
        Check if the current temperature is in tolerance to the target temperature.
        '''
        temp_tar = self._dwell_array[self._current_dwell_index].tar_temp
        tolerance = DbDwells.temp_tolerance
        return abs(temp_now - temp_tar) <= tolerance

    #region Transitions
    def _state_after_waiting(self) -> Literal[DwellState.PENDING]:
        return DwellState.PENDING

    def _state_after_pending(self) -> Literal[DwellState.WAITING, DwellState.ALARM, DwellState.FINISHED]:
        if self._dwell_array[self._current_dwell_index].alarm:
            return DwellState.ALARM
        else:
            return DwellState.FINISHED \
                if self._last_dwell_check() else DwellState.WAITING

    def _state_after_alarm(self) -> Literal[DwellState.WAITING, DwellState.FINISHED]:
        return DwellState.FINISHED \
            if self._last_dwell_check() else DwellState.WAITING

    # Helper methods for state transition
    def _last_dwell_check(self) -> bool:
        return self._current_dwell_index + 1 >= len(self._dwell_array)

    def _to_waiting_state(self) -> list:
        self._current_dwell_index += 1
        self.rest_time_s = self._dwell_array[self._current_dwell_index].tar_time_s
        self._dwell_state = DwellState.WAITING
        return [DwellAdvancedEvent(dwell_index=self._current_dwell_index)]

    def _to_pending_state(self) -> list:
        self._dwell_state = DwellState.PENDING
        return []

    def _to_alarm_state(self) -> list:
        self._dwell_state = DwellState.ALARM
        return [AlarmTriggeredEvent(dwell_index=self._current_dwell_index)]
    
    def _to_finished_state(self) -> list:
        self._current_dwell_index = -1
        self.rest_time_s = 0
        self._dwell_state = DwellState.FINISHED
        return [AllDwellsFinishedEvent()]
    #endregion Transitions

    @property
    def rest_time_s(self) -> int:
        return self._rest_time_s

    @rest_time_s.setter
    def rest_time_s(self, new_value) -> None:
        if new_value < 0:
            raise ValueError ("new rest time value < 0")
        self._rest_time_s = new_value

    #region DwellArray Manipulation
    @property
    def tar_temp(self):
        return self._dwell_array[self._current_dwell_index].tar_temp

    @tar_temp.setter
    def tar_temp(self, new_temp: float):
        if new_temp < 0:
            raise ValueError ("new target value < 0")
        if new_temp > 120:
            raise ValueError ("new target value > 120")

        self._dwell_array[self._current_dwell_index].tar_temp = new_temp
        self.tar_temp_changed.emit(new_temp)
        self.logger.info(f'dwell_array[{self._current_dwell_index}].tar_temp = {new_temp}')

    def set_dwell_temp(self, dwell_index: int, new_temp: float):
        if new_temp < 0:
            raise ValueError ("new target value < 0")
        if new_temp > 120:
            raise ValueError ("new target value > 120")

        self._dwell_array[dwell_index].tar_temp = new_temp
        self.logger.info(f'dwell_array[{dwell_index}].tar_temp = {new_temp}')

    def set_dwell_time(self, dwell_index: int, new_time: int):
        if new_time < 0:
            raise ValueError ("new target value < 0")

        self._dwell_array[dwell_index].tar_time_s = new_time
        self.logger.info(f'dwell_array[{dwell_index}].tar_time_s = {new_time}')

    @property
    def tar_time_s(self):
        return self._dwell_array[self._current_dwell_index].tar_time_s
    
    @tar_time_s.setter
    def tar_time_ds(self, new_time: int):
        if new_time < 0:
            raise ValueError ("new target value < 0")

        self._dwell_array[self._current_dwell_index].tar_time_ds = new_time
        self.logger.info(f'dwell_array[{self._current_dwell_index}].tar_time_ds = {new_time}')
    #endregion DwellArray Manipulation

    #region Move Dwells # TODO: These need to create events 
    def dwell_up(self, obj) -> list:
        index = next(i for i, x in enumerate(self._dwell_array) if x is obj)
        if index > 1:
            del self._dwell_array[index]
            self._dwell_array.insert(index -1, obj)
        return self._dwell_array

    def dwell_down(self, obj) -> list:
        index = next(i for i, x in enumerate(self._dwell_array) if x is obj)
        if index < len(self._dwell_array) -2:
            del self._dwell_array[index]
            self._dwell_array.insert(index +1, obj)
        return [DwellArrayChangedEvent(self._dwell_array)]

    def dwell_new(self, obj) -> list:
        index = next(i for i, x in enumerate(self._dwell_array) if x is obj)
        self._dwell_array.insert(index +1, Dwell(None, None, False))
        return [DwellArrayChangedEvent(self._dwell_array)]

    def dwell_delete(self, obj) -> list:
        index = next(i for i, x in enumerate(self._dwell_array) if x is obj)
        if (len(self._dwell_array) <= 2):
            print("Error: There can not be less than 2 dwells")
            map(lambda d: d.makeBound(), self._dwell_array)
            return
        del self._dwell_array[index]
        return [DwellArrayChangedEvent(self._dwell_array)]
    #endregion Move Dwells