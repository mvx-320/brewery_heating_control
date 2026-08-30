import time, logging
from PyQt5.QtCore import QThread
from simulation.sim_engine import SimEngine


class ThreadSimSer(QThread):

    def __init__(self, mash, fill, cook):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.info('ThreadSimSer initializing...')
        self.mash = mash
        self.fill = fill
        self.cook = cook
        self.sim_engine = SimEngine(mash, fill, cook)

        self.running = True
        self.interval = 1  # in s
        # self.previousSecs = 0.0

    def run(self):
        while self.running:
            try:
                self.sim_engine.step_seconds(1)

                self.logger.info(f"Simulated temp: {self.mash.temp_now:.1f};{self.fill.temp_now:.1f};{self.cook.temp_now:.1f};OK")
            except Exception as e:
                self.logger.warning(f"Simulated error: {str(e)}")
            
            time.sleep(self.interval)

    def advance_to(self, target_s):
        self.sim_engine.advance_to(target_s)

    def forward(self, delta_s: float):
        self.sim_engine.forward(delta_s)

    def stop(self):
        self.running = False

