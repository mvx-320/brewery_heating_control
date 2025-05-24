import time, logging
from PyQt5.QtCore import QThread


class ThreadMockupSer(QThread):

    def __init__(self, mash, fill, cook):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.mash = mash
        self.fill = fill
        self.cook = cook
        self.running = True
        self.interval = 1  # in s
        self.intervalLock = 60
        self.previousSecs = 0.0
        self.previousLock = 0.0

    def run(self):
        self.mash.temp_now = 20
        self.fill.temp_now = 20
        self.cook.temp_now = 20

        while self.running:
            try:
                currentSecs = time.time()
                if currentSecs - self.previousSecs >= self.interval:
                    self.previousSecs = currentSecs

                    self.simulate_heating(self.mash)
                    self.simulate_heating(self.fill)
                    self.simulate_heating(self.cook)

                    if currentSecs - self.previousLock >= self.intervalLock:
                        self.previousLock = currentSecs
                        self.logger.info(f"Mock Temp: {self.mash.temp_now:.1f};{self.fill.temp_now:.1f};{self.cook.temp_now:.1f};OK")
                        print(f"Mock Temp: {self.mash.temp_now:.1f};{self.fill.temp_now:.1f};{self.cook.temp_now:.1f};OK")
            except Exception as e:
                self.logger.warning(f"Mock error: {str(e)}")
                print(f"Mock error: {str(e)}")

    def simulate_heating(self, pot):
        power_ratio = pot.heat_val / 3500.0  # normalized [0,1]
        ambient = 20.0
        max_temp = 120.0
#        if not hasattr(pot, 'temp_now'):
#            pot.temp_now = ambient
        delta = (max_temp - pot.temp_now) * power_ratio * 0.005  - (pot.temp_now - ambient) * 0.01 # simple heating model
        pot.temp_now = min(max_temp, pot.temp_now + delta)

    def stop(self):
        self.running = False
