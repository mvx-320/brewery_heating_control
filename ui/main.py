import sys
import ui.interface as interface
from PyQt5 import QtCore, QtGui, QtWidgets

# TODO: That has to be put in ./main.py

if __name__ == "__main__":

                

    # Remove function
    def printDwellArray(array: list[dwell_frame.Dwell]):
        print('RASTEN:')
        for index, dwell in enumerate(array): 
            print(f'index: {index}; temp: {dwell.tar_temp}°C; time: {dwell.tar_time}min; alarm: {dwell.alarm}')
        

    app = QtWidgets.QApplication(sys.argv)

    MainWindow = QtWidgets.QMainWindow()
    ui = interface.Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.show()


    sys.exit(app.exec_())
