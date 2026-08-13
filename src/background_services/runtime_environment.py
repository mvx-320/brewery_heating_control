import sys
import logging
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal

# Projektverzeichnis zum Python-Pfad hinzufügen
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from components.pots.dwell_pot import DwellPot


class DwellRuntimeEnvironment(QObject):
    """
    Runtime Environment für die Mash-Prozess-Steuerung.

    Steuert den gesamten Maischprozess:
    - Startet Heat Regulation und Timer für jeden Dwell
    - Wechselt automatisch zum nächsten Dwell wenn Zeit abgelaufen
    - Löst Alarm aus wenn gewünscht
    - Stoppt den Prozess
    """

    mash_process_completed = pyqtSignal()
    alarm_triggered = pyqtSignal(int)  # dwell_index

    def __init__(self, mash_pot, time_mash_thread):
        super().__init__()
        self.mash_pot = mash_pot
        self.time_mash_thread = time_mash_thread
        self.logger = logging.getLogger(__name__)

        self.is_running = False

        self.mash_pot.dwell_finished.connect(self._on_dwell_finished)

        self.logger.info("DwellRuntimeEnvironment initialized")

    # region public API
    def start_mash(self):
        if self.is_running:
            return

        self.logger.info("Mash started")
        self.is_running = True
        self.mash_pot.current_dwell_index = 0
        self._activate_dwell(0)

    def stop_mash(self):
        self.is_running = False
        self.time_mash_thread.stop()
        self.mash_pot.heat_regulation = False
        self.mash_pot.heat_val = 0.0
        self.mash_pot.temp_tar = 0
        self.mash_pot.rest_time_ds = 0
        self.mash_pot.run_state = 0
        self.mash_pot.current_dwell_index = -1
        self.logger.info("Mash stopped")

    def confirm_alarm(self):
        self.logger.info("Alarm confirmed, proceeding to next dwell")
        self._next_dwell()
    # endregion

    # region internal
    def _on_dwell_finished(self):
        if not self.is_running:
            return

        current_index = self.mash_pot.current_dwell_index
        dwell_array = self.mash_pot.get_dwell_array()
        current_dwell = dwell_array[current_index]

        if current_dwell.alarm:
            self.logger.info(f"Dwell {current_index} finished - Alarm activated, waiting for confirmation")
            self.alarm_triggered.emit(current_index)
        else:
            self._next_dwell()

    def _activate_dwell(self, index):
        dwell_array = self.mash_pot.get_dwell_array()
        dwell = dwell_array[index]

        self.time_mash_thread.stop()

        self.mash_pot.temp_tar = dwell.tar_temp

        self.mash_pot.run_state = 1

        if dwell.tar_time_ds is not None and dwell.tar_time_ds > 0:
            self.mash_pot.rest_time_ds = dwell.tar_time_ds
            self.mash_pot.dwell_progress_changed.emit(index, 0, dwell.tar_time_ds, dwell.tar_time_ds)
        else:
            self.mash_pot.rest_time_ds = 0

        self.mash_pot.heat_regulation = True

        self.logger.info(f"Dwell {index} activated: temp={dwell.tar_temp}, time_ds={dwell.tar_time_ds}")

    def _next_dwell(self):
        current_index = self.mash_pot.current_dwell_index
        dwell_array = self.mash_pot.get_dwell_array()

        if current_index < len(dwell_array) - 1:
            next_index = current_index + 1
            self.mash_pot.current_dwell_index = next_index
            self._activate_dwell(next_index)
        else:
            self._finish_mash()

    def _finish_mash(self):
        self.time_mash_thread.stop()
        self.mash_pot.heat_regulation = False
        self.mash_pot.heat_val = 0.0
        self.is_running = False
        self.logger.info("Mash process finished")
        self.mash_process_completed.emit()
    # endregion
