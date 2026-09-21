from PyQt5.QtCore import QTimer, QObject

from src.services.db.db_pid_values import PidValuesService


class PeriodHeatReg(QObject):
    
    def __init__(self, mash, fill, cook, time_mash_thread, time_cook_thread):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run)
        
        self.mash = mash
        self.fill = fill
        self.cook = cook
        
        self.time_mash_thread = time_mash_thread
        self.time_cook_thread = time_cook_thread

    def regulation_tick(self):
        # MASH #######################################################################################################
        if self.mash.heat_regulation:
            self.mash.heat_val, _ = self.mash.pid.calculate(self.mash.temp_tar, self.mash.temp_now)
            if self.mash.run_state == 1 and self.mash.temp_now >= self.mash.temp_tar:
                if self.mash.rest_time_ds is not None and self.mash.rest_time_ds > 0:
                    self.time_mash_thread.start()
                    self.mash.run_state = 2
                else:
                    self.mash.run_state = 2
                    self.mash.dwell_finished.emit()
        else:
            self.mash.heat_val = 0.0

        # FILL #######################################################################################################
        if self.fill.heat_regulation:
            self.fill.heat_val, _ = self.fill.pid.calculate(self.fill.temp_tar, self.fill.temp_now)
        else:
            self.fill.heat_val = 0.0

        # COOK #######################################################################################################
        if self.cook.heat_regulation:
            self.cook.heat_val, _ = self.cook.pid.calculate(self.cook.temp_tar, self.cook.temp_now)
            if self.cook.run_state == 1 and self.cook.temp_now >= self.cook.temp_tar:
                if self.cook.rest_time_ds is not None and self.cook.rest_time_ds > 0:
                    self.time_cook_thread.start()
                    self.cook.run_state = 2
                else:
                    self.cook.run_state = 2
                    self.cook.dwell_finished.emit()
        else:
            self.cook.heat_val = 0.0
        ##############################################################################################################


    def run(self):
        self.regulation_tick()
                    
            
    def start(self):
        self.timer.start(int(PidValuesService.dt * 1000))
                 
    def stop(self):
        self.timer.stop()