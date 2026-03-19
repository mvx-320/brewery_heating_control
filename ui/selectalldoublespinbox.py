from PyQt5 import QtWidgets, QtCore, QtGui

# TODO: Kann das weg?
class SelectAllDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, parent=None): 
        super().__init__(parent)
        self.spinBox_font = QtGui.QFont()
        self.spinBox_font.setPointSize(16)
        self.setFont(self.spinBox_font)
        self.setStyleSheet("\
                            background-color: rgba(255, 255, 255,60);\
                            border: none;\
                            border-radius: 8px;\
                           ")
        self.setLocale(QtCore.QLocale(QtCore.QLocale.German, QtCore.QLocale.Germany))
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.setMinimumHeight(40)
        self.setDecimals(1)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        QtCore.QTimer.singleShot(0, self.lineEdit().selectAll)

        