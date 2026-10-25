from PyQt5.QtCore import QTimer, QObject

from src.services.db.db_pid_values import DbPidValues


class PeriodHeatReg(QObject):
    
    def __init__(self, mash, fill, cook, time_cook_thread):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run)
        
        self.mash = mash
        self.fill = fill
        self.cook = cook
        
        # self.time_mash_thread = time_mash_thread
        self.time_cook_thread = time_cook_thread


    def regulation_tick(self):
        # MASH ########################################################################################################
        # Logic is in DwellController and way more clear to read

        # FILL ########################################################################################################
        if self.fill.heat_regulation:
            self.fill.heat_val, _ = self.fill.pid.calculate(self.fill.temp_tar, self.fill.temp_now)
        else:
            self.fill.heat_val = 0.0

        # COOK ########################################################################################################
        if self.cook.heat_regulation:
            self.cook.heat_val, _ = self.cook.pid.calculate(self.cook.temp_tar, self.cook.temp_now)
            if self.cook.run_state == 1 and self.cook.temp_now >= self.cook.temp_tar:
                if self.cook.rest_time_ds is not None and self.cook.rest_time_ds > 0:
                    self.time_cook_thread.start()
                    self.cook.run_state = 2
                else:
                    self.cook.dwell_finished.emit()
        else:
            self.cook.heat_val = 0.0
        ###############################################################################################################


    def run(self):
        self.regulation_tick()
                    
            
    def start(self):
        self.timer.start(int(DbPidValues.dt * 1000))
                 
    def stop(self):
        self.timer.stop()