from dataclasses import dataclass
@dataclass
class MashStartedEvent:
    pass
@dataclass
class HeatValChangedEvent: # TODO: Add pid_events and move this one out
    heat_val: float
@dataclass
class DwellArrayChangedEvent:
    dwell_array: list
@dataclass
class DwellProgressChangedEvent:
    dwell_index: int
    rest_time_s: int
    total_time_s: int

@dataclass
class AlarmTriggeredEvent:
    dwell_index: int

@dataclass
class DwellAdvancedEvent:
    dwell_index: int
    new_tar_temp: float

@dataclass # TODO: Not used yet
class AllDwellsFinishedEvent:
    pass