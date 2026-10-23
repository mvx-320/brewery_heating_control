from PyQt5.QtCore import QObject, pyqtSignal

class DwellSignals(QObject):
    dwell_advanced = pyqtSignal(int)  