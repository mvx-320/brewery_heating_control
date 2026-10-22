from typing import Literal

from src.components.enums.dwell_state import DwellState
from src.components.pots.pot import Pot
from src.controls.pid_controller import PidController
from src.dtos.dwell_events import \
    DwellProgressChangedEvent, \
    AlarmTriggeredEvent
from src.services.db.db_dwells import DbDwells


class DwellController:
    '''
    Controller is not a QObject, no relations to Qt (signals, slots, ...).
    No event loop just the logic methods to control the dwells.
    '''

    def __init__(self, pot : Pot):
        # TODO: Maybe add Logger here
        self._pot = pot
        self._pid_controller = PidController(pot) 

        self._dwell_state = DwellState.IDLE
        self._current_dwell_index = -1
        self._rest_time_s = 0

        # DB
        self._dwell_array = DbDwells.dwell_array


    def tick(self):
        '''
        Execute 1/s
        '''
        events = []
        events += self.pid_controller.tick()

        match self._dwell_state:
            case DwellState.IDLE:
                return events

            case DwellState.WAITING:
                if self._temp_in_tolerance(self._pot.temp_now):
                    next_state = self._state_after_waiting()
                    match next_state:
                        case DwellState.PENDING:
                            events += self._to_pending_state()
                return events

            case DwellState.PENDING:
                self.rest_time_s -= 1
                events.append(DwellProgressChangedEvent(
                    dwell_index = self._current_dwell_index,
                    tar_time_s = self._dwell_array[self._current_dwell_index].tar_time_s,
                    elapsed_s = self._dwell_array[self._current_dwell_index].tar_time_s - self.rest_time_s
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

                # Transition
                if "alarm_confirmed":
                    next_state = self._state_after_alarm()
                    match next_state:
                        case DwellState.WAITING:
                            events += self._to_waiting_state()
                        case DwellState.FINISHED:
                            events += self._to_finished_state()
                return events


    def _temp_in_tolerance(self, temp_now: float) -> bool:
        '''
        Check if the current temperature is in tolerance to the target temperature.
        '''
        temp_tar = self._dwell_array[self._current_dwell_index].tar_temp
        tolerance = DbDwells.temp_tolerance
        return abs(temp_now - temp_tar) <= tolerance

    #region State Transitions
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

    def _to_waiting_state(self):
        self._current_dwell_index += 1
        self.rest_time_s = self._dwell_array[self._current_dwell_index].tar_time_s
        self._dwell_state = DwellState.WAITING
        return []

    def _to_pending_state(self):
        self._dwell_state = DwellState.PENDING
        return []

    def _to_alarm_state(self):
        self._dwell_state = DwellState.ALARM
        return [AlarmTriggeredEvent(dwell_index=self._current_dwell_index)]
    
    def _to_finished_state(self):
        self._current_dwell_index = -1
        self.rest_time_s = 0
        self._dwell_state = DwellState.FINISHED
        return []
    #endregion

    @property
    def rest_time_s(self):
        return self._rest_time_s

    @rest_time_s.setter
    def rest_time_s(self, new_value):
        if new_value < 0:
            raise ValueError ("new rest time value < 0")
        self._rest_time_s = new_value