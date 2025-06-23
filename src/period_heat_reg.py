from PyQt5.QtCore import QThread, QTimer, QObject, pyqtSignal
import pid_controller
import time, logging


class PeriodHeatReg(QObject):
    
    def __init__(self, mash, fill, cook, time_mash_thread, time_cook_thread, interval_ms= 500):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run)
        self.interval_ms = interval_ms
        
        self.mash = mash
        self.fill = fill
        self.cook = cook
        
        self.time_mash_thread = time_mash_thread
        self.time_cook_thread = time_cook_thread
        
        self.logger.info("PeriodHeatReg initialized")


    def run(self):
        if self.mash.heat_regulation:
            self.mash.heat_val, pid_active = self.mash.pid.calculate(self.mash.temp_tar, self.mash.temp_now)
            if self.mash.run_state == 1 and pid_active:
                self.time_mash_thread.start()
                self.mash.run_state = 2
                self.logger.info(f"Mash timer started - Target: {self.mash.temp_tar}°C, Current: {self.mash.temp_now:.1f}°C, Heat: {self.mash.heat_val}W")
        else:
            self.mash.heat_val = 0

        if self.fill.heat_regulation:
            self.fill.heat_val, pid_active = self.fill.pid.calculate(self.fill.temp_tar, self.fill.temp_now)
            if self.fill.heat_val > 0:
                self.logger.info(f"Fill heating - Target: {self.fill.temp_tar}°C, Current: {self.fill.temp_now:.1f}°C, Heat: {self.fill.heat_val}W")
        else:
            self.fill.heat_val = 0
            self.cook.heat_val, pid_active = self.cook.pid.calculate(self.cook.temp_tar, self.cook.temp_now)
            if self.cook.run_state == 1 and pid_active:
                self.time_cook_thread.start()
                self.cook.run_state = 2
                self.logger.info(f"Cook timer started - Target: {self.cook.temp_tar}°C, Current: {self.cook.temp_now:.1f}°C, Heat: {self.cook.heat_val}W")
        else:
            self.cook.heat_val = 0
                    
    def isRunning(self):
        return self.timer.isActive()
            
    def start(self):
        self.timer.start(self.interval_ms)
        self.logger.info("PeriodHeatReg started")
                 
    def stop(self):
        self.timer.stop()
        self.logger.info("PeriodHeatReg stopped")
        
        
class PeriodTimePot(QObject):
    
    def __init__(self, pot):
        super().__init__()        
        self.logger = logging.getLogger(__name__)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run)
        
        self.pot = pot
        self.logger.info(f"PeriodTimePot initialized for {pot.name}")
                
    def run(self):
        self.pot.act_time -= self.pot.interval_s
        
    def isRunning(self):
        return self.timer.isActive()
        
    def start(self):
        self.timer.start(int(self.pot.interval_s) *1000)
        self.logger.info(f"{self.pot.name} timer started")

    def pause(self):
        self.timer.stop()
        self.logger.info(f"{self.pot.name} timer paused")
