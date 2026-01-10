import sys
import interface
from PyQt5 import QtCore, QtGui, QtWidgets
import dwell_frame


objects = [
    dwell_frame.Dwell(50.0, 30.0, True),
    dwell_frame.Dwell(60.0, 20.0, False),
    dwell_frame.Dwell(60.0, 20.0, False),
    dwell_frame.Dwell(60.0, 20.0, False),
    dwell_frame.Dwell(60.0, 20.0, False),
    dwell_frame.Dwell(60.0, None, False),
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
        scroll = ui.steps_scroll.verticalScrollBar()
        print(f'Scroll-Value: {scroll.value()}')
        clear_steps()
        
        for i, obj in enumerate(objects):

            frame = dwell_frame.DwellFrame(i, obj) 

            frame.temp_changed.connect(temp_changed_handler)
            frame.time_changed.connect(time_changed_handler)
            frame.up_clicked.connect(up_clicked_handler)
            frame.down_clicked.connect(down_clicked_handler)
            frame.new_clicked.connect(new_clicked_handler)
            frame.delete_clicked.connect(delete_clicked_handler)
            
            ui.dwell_layout.addWidget(frame)

        ui.dwell_layout.addStretch()
        
    def temp_changed_handler(tar_temp):
        print(tar_temp)

    def time_changed_handler(tar_time):
        print(tar_time)
        
    def up_clicked_handler(obj):
        index = next(i for i, x in enumerate(objects) if x is obj)
        if index != 0:
            del objects[index]
            objects.insert(index -1, obj)
            update_steps(objects)

    def down_clicked_handler(obj):
        index = next(i for i, x in enumerate(objects) if x is obj)
        if index < len(objects) -1:
            del objects[index]
            objects.insert(index +1, obj)
            update_steps(objects)
        
    def new_clicked_handler(obj):
        index = next(i for i, x in enumerate(objects) if x is obj)
        objects.insert(index +1, dwell_frame.Dwell(None, None, False))
        update_steps(objects)

    def delete_clicked_handler(obj):
        index = next(i for i, x in enumerate(objects) if x is obj)
        del objects[index]
        update_steps(objects)

    app = QtWidgets.QApplication(sys.argv)

    MainWindow = QtWidgets.QMainWindow()
    ui = interface.Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.show()

    # TODO: I should clean up the dwells from the interface.ui
    # clear_steps()
    update_steps(objects)

    sys.exit(app.exec_())
