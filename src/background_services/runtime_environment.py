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
    
    Später wird diese Klasse einen Thread starten, der:
    - Die restliche Zeit der Dwells herunterzählt
    - Popups öffnet, wenn etwas zu tun ist
    - Den Braualarm aktiviert
    - In den nächsten Dwell wechselt
    - Die gesamte Logik des Prozesses übernimmt
    """
    
    def __init__(self, mash_pot):
        super().__init__()
        self.mash_pot = mash_pot
        self.logger = logging.getLogger(__name__)
        
        self.is_running = False
        self.is_paused = False
        
        self.logger.info("DwellRuntimeEnvironment initialized")
    
    # region state management
    def start_mash(self):
        DwellPot.next_dwell(self.mash_pot)