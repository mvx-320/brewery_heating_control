from PyQt5.QtCore import QObject, QTimer

class PeriodTimePot(QObject):
    
    def __init__(self, pot):
        super().__init__()        
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run)
        
        self.pot = pot
        
                
    def run(self):
        self.pot.rest_time -= int(self.pot.interval_s)
        
        
    def start(self):
        self.timer.start(self.pot.interval_s *1000)

    def pause(self):
        self.timer.stop()