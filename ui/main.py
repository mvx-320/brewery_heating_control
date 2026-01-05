import sys
import interface
from PyQt5 import QtCore, QtGui, QtWidgets
import dwell_frame


objects = [
    dwell_frame.Dwell(50, 30, True),
    dwell_frame.Dwell(60, 20, False),
    dwell_frame.Dwell(60, 20, False),
    dwell_frame.Dwell(60, 20, False),
    dwell_frame.Dwell(60, 20, False),
    dwell_frame.Dwell(60, 20, False),
]


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
        
        for i, obj in enumerate(objects):
            frame = dwell_frame.DwellFrame(i, obj) 

            # frame.alarm_clicked.connect(alarm_clicked_handler)
            
            ui.dwell_layout.addWidget(frame)

        ui.dwell_layout.addStretch()
        
    # def alarm_clicked_handler(obj):
    #     # print(obj)
    #     # obj.toggleAlarm()
    #     update_steps(objects)

    app = QtWidgets.QApplication(sys.argv)

    MainWindow = QtWidgets.QMainWindow()
    ui = interface.Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.show()

    # clear_steps()
    update_steps(objects)

    sys.exit(app.exec_())
