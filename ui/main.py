import sys
import interface
from PyQt5 import QtCore, QtGui, QtWidgets
import dwell_frame


dwell_array: list[dwell_frame.Dwell] = [
    dwell_frame.Dwell(50.0, None, True),
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
                
    def update_steps(dwell_array):
        scroll = ui.steps_scroll.verticalScrollBar()
        print(f'Scroll-Value: {scroll.value()}')
        clear_steps()
        
        dwell_amount = len(dwell_array)
        for i, obj in enumerate(dwell_array):

            frame = dwell_frame.DwellFrame(i, dwell_amount, obj) 

            frame.temp_changed.connect(temp_changed_handler)
            frame.time_changed.connect(time_changed_handler)
            frame.up_clicked.connect(up_clicked_handler)
            frame.down_clicked.connect(down_clicked_handler)
            frame.new_clicked.connect(new_clicked_handler)
            frame.delete_clicked.connect(delete_clicked_handler)
            
            ui.dwell_layout.addWidget(frame)

        ui.dwell_layout.addStretch()
        
    def temp_changed_handler(index, value):
        # TODO: Muss bei pots.py geändert werden
        dwell_array[index].tar_temp = value
        printDwellArray(dwell_array)

    def time_changed_handler(index, value):
        # TODO: Muss bei pots.py geändert werden
        dwell_array[index].tar_time = value
        printDwellArray(dwell_array)

    # Remove function
    def printDwellArray(array: list[dwell_frame.Dwell]):
        print('RASTEN:')
        for index, dwell in enumerate(array): 
            print(f'index: {index}; temp: {dwell.tar_temp}°C; time: {dwell.tar_time}min; alarm: {dwell.alarm}')
        
    def up_clicked_handler(obj):
        index = next(i for i, x in enumerate(dwell_array) if x is obj)
        if index > 1:
            del dwell_array[index]
            dwell_array.insert(index -1, obj)
            update_steps(dwell_array)

    def down_clicked_handler(obj):
        index = next(i for i, x in enumerate(dwell_array) if x is obj)
        if index < len(dwell_array) -2:
            del dwell_array[index]
            dwell_array.insert(index +1, obj)
            update_steps(dwell_array)
        
    def new_clicked_handler(obj):
        index = next(i for i, x in enumerate(dwell_array) if x is obj)
        dwell_array.insert(index +1, dwell_frame.Dwell(None, None, False))
        update_steps(dwell_array)

    def delete_clicked_handler(obj):
        index = next(i for i, x in enumerate(dwell_array) if x is obj)
        if (len(dwell_array) <= 2):
            print("Error: There can not be less than 2 dwells")
            map(lambda d: d.makeBound(), dwell_array)
            return
        del dwell_array[index]
        update_steps(dwell_array)

    app = QtWidgets.QApplication(sys.argv)

    MainWindow = QtWidgets.QMainWindow()
    ui = interface.Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.show()

    # TODO: I should clean up the dwells from the interface.ui
    # clear_steps()
    update_steps(dwell_array)

    sys.exit(app.exec_())
