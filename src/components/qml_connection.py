import os, sys, datetime

from PySide6.QtCore import QObject, Slot, Signal, QTimer, QUrl

class MainWindow(QObject):
    setText = Signal(str)
    setDwells = Signal(list)

    def __init__(self):
        QObject.__init__(self)
        self.dwells = [
                {"temp": 50, "time": 20, "alarm": false},
                {"temp": 60, "time": 10, "alarm": true},
                {"temp": 65, "time": 30, "alarm": false},
                ]
        # self.setDwells.emit(self._dwells)


    @Slot(str)
    def function(self, text):
        self.setText.emit(">" + text + "<")

