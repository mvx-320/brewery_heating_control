from dataclasses import dataclass
from src.components.enums.dwell_state import DwellState
@dataclass
class MashStartedEvent:
    pass
@dataclass
class HeatValChangedEvent: # TODO: Add pid_events and move this one out
    heat_val: float
@dataclass
class DwellStateChangedEvent:
    new_state: DwellState
@dataclass
class DwellArrayChangedEvent:
    dwell_array: list
@dataclass
class DwellProgressChangedEvent:
    dwell_index: int
    rest_time_s: int
    total_time_s: int
@dataclass
class AlarmToggledEvent:
    dwell_index: int
    alarm_active: bool
@dataclass
class DwellAdvancedEvent:
    dwell_index: int
    new_tar_temp: float
@dataclass # TODO: Not used yet
class AllDwellsFinishedEvent:
    pass