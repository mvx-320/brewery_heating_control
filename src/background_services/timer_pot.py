from PyQt5.QtCore import QObject, QTimer

class PeriodTimePot(QObject):
    
    def __init__(self, pot):
        super().__init__()        
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run)
        
        self.pot = pot
        
                
    def run(self):
        self.pot.rest_time -= self.pot.interval_ds

        if self.pot.rest_time <= 0:
            self.timer.stop()
            self.pot.dwell_finished.emit()
            return

        tar_time = self.pot.tar_time_ds
        if tar_time and tar_time > 0:
            elapsed = tar_time - self.pot.rest_time
            self.pot.dwell_progress_changed.emit(self.pot.current_dwell_index, elapsed, tar_time, self.pot.rest_time)


    def start(self):
        self.timer.start(self.pot.interval_ds * 100)  # ds * 100 = ms

    def stop(self):
        self.timer.stop()