import sys
import interface
from PyQt5 import QtCore, QtGui, QtWidgets
import dwell_frame




if __name__ == "__main__":

    def clear_steps():
        layout = ui.dwell_layout
        
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
                
    def update_steps(objects):
        clear_steps()
        
        for obj in objects:
            frame = dwell_frame.DwellFrame(obj) 
            ui.dwell_layout.addWidget(frame)

        ui.dwell_layout.addStretch()

    app = QtWidgets.QApplication(sys.argv)

    MainWindow = QtWidgets.QMainWindow()
    ui = interface.Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.show()

    clear_steps()

    objects = [
        dwell_frame.Dwell(50, 30, True),
        dwell_frame.Dwell(60, 20, False),
        dwell_frame.Dwell(60, 20, False),
        dwell_frame.Dwell(60, 20, False),
        dwell_frame.Dwell(60, 20, False),
        dwell_frame.Dwell(60, 20, False),
    ]

    update_steps(objects)

    sys.exit(app.exec_())
