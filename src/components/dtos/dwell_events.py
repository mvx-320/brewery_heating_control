@dataclass
class AlarmTriggeredEvent:
    dwell_index: int

@dataclass
class DwellAdvancedEvent:
    dwell_index: int

@dataclass
class AllDwellsFinishedEvent:
    pass