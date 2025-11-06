import os, sys, datetime

from PySide6.QtCore import QObject, Slot, Signal, QTimer, QUrl

class MainWindow(QObject):
    def __init__(self):
        QObject.__init__(self)

    setText = Signal(str)

    @Slot(str)
    def function(self, text):
        self.setText.emit(">" + text + "<")
