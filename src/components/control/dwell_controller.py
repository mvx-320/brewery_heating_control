from src.components.enums.dwell_state import DwellState
from src.components.enums.pot_type import PotType
from src.services.db.db_dwells import DbDwells


class DwellController:
    '''
    Controller is not a QObject, no relations to Qt (signals, slots, ...).
    No event loop just the logic methods to control the dwells.
    '''

    def __init__(self, pot_type : PotType = PotType.MASH):
        # TODO: Maybe add Logger here
        self.pot_type = pot_type

        self._dwell_state = DwellState.IDLE
        self._current_dwell_index = -1
        self._rest_time_s = 0

        # DB
        self._dwell_array = DbDwells.dwell_array


    def tick(self):
        '''
        Execute 1/s
        '''
        self._rest_time_s -= 1 # TODO: Emit signal for UI (prev: pot.dwell_progress_changed) (now DwellProgressChangedEvent in dwell_events.py)


        if self._rest_time_s <= 0:
            # TODO: Emit DwellFinished signal
            pass





    @property
    def rest_time_s(self):
        return self._rest_time_s

    @rest_time_s.setter
    def rest_time_s(self, new_value):
        if new_value < 0:
            raise ValueError ("new rest time value < 0")
        self._rest_time_s = new_value