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

    mash_finished = pyqtSignal()

    def __init__(self, mash_pot):
        super().__init__()
        self.mash_pot = mash_pot
        self.logger = logging.getLogger(__name__)

        self.is_running = False

        self.mash_pot.run_state_changed.connect(self._on_run_state_changed)

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
        self.mash_pot.heat_regulation = False
        self.mash_pot.heat_val = 0
        self.mash_pot.temp_tar = 0
        self.mash_pot.rest_time = 0
        self.mash_pot.run_state = 0
        self.mash_pot.current_dwell_index = -1
        self.logger.info("Mash stopped")
    # endregion

    # region internal
    def _on_run_state_changed(self, new_state):
        if not self.is_running:
            return

        if new_state == 3:
            current_index = self.mash_pot.current_dwell_index
            dwell_array = self.mash_pot.get_dwell_array()
            current_dwell = dwell_array[current_index]

            if current_dwell.alarm:
                self.logger.info(f"ALARM: Dwell {current_index} - Zeit abgelaufen!")

            self._next_dwell()

    def _activate_dwell(self, index):
        dwell_array = self.mash_pot.get_dwell_array()
        dwell = dwell_array[index]

        self.mash_pot.tar_temp = dwell.tar_temp

        if dwell.tar_time is not None:
            self.mash_pot.rest_time = dwell.tar_time
        else:
            self.mash_pot.rest_time = 0

        self.mash_pot.run_state = 1
        self.mash_pot.heat_regulation = True

        self.logger.info(f"Dwell {index} activated: temp={dwell.tar_temp}, time={dwell.tar_time}")

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
        self.mash_pot.heat_regulation = False
        self.mash_pot.heat_val = 0
        self.is_running = False
        self.logger.info("Maischprozess abgeschlossen")
        self.mash_finished.emit()
    # endregion
