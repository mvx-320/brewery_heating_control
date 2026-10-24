import time, logging
from PyQt5.QtCore import QThread, QTimer
from simulation.sim_engine import SimEngine


class DriverSimulation(QThread):

    def __init__(self, mash, fill, cook):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.info('DriverSimulation initializing...')
        self.mash = mash
        self.fill = fill
        self.cook = cook
        self.sim_engine = SimEngine(mash, fill, cook)

        self.paused = False

    def run(self):
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self._step)

        self.timer.start()
        self.exec_() # starts thread event loop so the timer runs

    def _step(self): # Timer in the Thread execute 1/s
        if self.paused: 
            return # Stoop if simulation is paused
        try:
            self.sim_engine.step_seconds(1)

            self.logger.info(f"Simulated temp: {self.mash.temp_now:.1f};{self.fill.temp_now:.1f};{self.cook.temp_now:.1f};OK")
        except Exception as e:
            self.logger.warning(f"Simulated error: {str(e)}")

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.quit() # stops the exec_() event loop and the thread. The timer is stopped automatically when the thread is stopped.