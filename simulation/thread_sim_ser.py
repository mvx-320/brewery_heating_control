import time, logging
from PyQt5.QtCore import QThread, QMutex, QMutexLocker
from simulation.sim_engine import SimEngine


class ThreadSimSer(QThread):

    def __init__(self, mash, fill, cook, regulation_tick):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.info('ThreadSimSer initializing...')
        self.mash = mash
        self.fill = fill
        self.cook = cook
        self.sim_engine = SimEngine(mash, fill, cook)
        self.regulation_tick = regulation_tick
        self.forward_lock = QMutex()
        self.pending_forward = 0

        self.running = True
        self.interval = 1  # in s
        # self.previousSecs = 0.0

    def tick(self):
            self.regulation_tick()
            self.sim_engine.step_seconds(1)


    def run(self):
        while self.running:
            with QMutexLocker(self.forward_lock):
                extra = self.pending_forward
                self.pending_forward = 0
            for _ in range(1 + extra):
                try:
                    self.tick()        

                    self.logger.info(f"Simulated temp: {self.mash.temp_now:.1f};{self.fill.temp_now:.1f};{self.cook.temp_now:.1f};OK")
                except Exception as e:
                    self.logger.warning(f"Simulated error: {str(e)}")
            time.sleep(self.interval)


    def request_forward(self, delta_s: int):
        with QMutexLocker(self.forward_lock):
            self.pending_forward += delta_s

    def stop(self):
        self.running = False

