from PyQt5.QtCore import QObject, QTimer, pyqtSignal

from src.components.pots.pot import Pot
from src.dtos.dwell_events import DwellArrayChangedEvent


class PeriodDwellController(QObject):
    events_ready = pyqtSignal(list)

    def __init__(self, pot : Pot, dwell_controller, pid_controller):
        super().__init__()
        self.pot = pot
        self.dwell_controller = dwell_controller
        self.pid_controller = pid_controller

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self._run)

        self.events_ready.emit([DwellArrayChangedEvent(self.dwell_controller.get_dwell_array())])


    def _run(self):
        events = []
        temp_now = self.pot.temp_now
        events += self.dwell_controller.tick(temp_now)
        events += self.pid_controller.tick(self.dwell_controller.temp_tar, temp_now)
        self.events_ready.emit(events)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()