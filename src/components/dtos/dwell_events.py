from dataclasses import dataclass

@dataclass
class DwellProgressChangedEvent:
    dwell_index: int
    target_time_s: int
    elapsed_time_s: int

@dataclass
class AlarmTriggeredEvent:
    dwell_index: int

@dataclass
class DwellAdvancedEvent:
    dwell_index: int

@dataclass
class AllDwellsFinishedEvent:
    pass