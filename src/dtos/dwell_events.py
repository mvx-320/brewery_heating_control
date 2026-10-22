from dataclasses import dataclass
# TODO: Look which event is needed
@dataclass
class HeatValChangedEvent:
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

@dataclass
class AllDwellsFinishedEvent:
    pass