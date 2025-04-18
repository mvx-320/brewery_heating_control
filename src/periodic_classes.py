
from PyQt5.QtCore import QTimer, QObject


class PeriodHeatReg(QObject):
    
    def __init__(self, mash, fill, cook, time_mash_thread, time_cook_thread, interval_ms= 500):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run)
        self.interval_ms = interval_ms
        
        self.mash = mash
        self.fill = fill
        self.cook = cook
        
        self.time_mash_thread = time_mash_thread
        self.time_cook_thread = time_cook_thread


    def run(self):
        if self.mash.heat_regulation:
            self.mash.heat_val, pid_active = self.mash.pid.calculate(self.mash.temp_tar, self.mash.temp_now)
            if self.mash.run_state == 1 and pid_active:
                self.time_mash_thread.start()
                self.mash.run_state = 2
        else:
            self.mash.heat_val = 0

        if self.fill.heat_regulation:
            self.fill.heat_val, pid_active = self.fill.pid.calculate(self.fill.temp_tar, self.fill.temp_now)
        else:
            self.fill.heat_val = 0

        if self.cook.heat_regulation:
            self.cook.heat_val, pid_active = self.cook.pid.calculate(self.cook.temp_tar, self.cook.temp_now)
            if self.cook.run_state == 1 and pid_active:
                self.time_cook_thread.start()
                self.cook.run_state = 2
        else:
            self.cook.heat_val = 0
                    
            
    def start(self):
        self.timer.start(self.interval_ms)
                 
    def stop(self):
        self.timer.stop()
        
        
class PeriodTimePot(QObject):
    
    def __init__(self, pot):
        super().__init__()        
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run)
        
        self.pot = pot
        
                
    def run(self):
        self.pot.act_time -= self.pot.interval_s
        
        
    def start(self):
        self.timer.start(self.pot.interval_s *1000)

    def pause(self):
        self.timer.stop()
