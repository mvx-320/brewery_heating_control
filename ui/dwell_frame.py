import sys
from PyQt5 import QtCore, QtGui, QtWidgets, Qt

class Dwell:
    def __init__(self, tar_temp: int, tar_time:int, alarm: bool):
        self.tar_temp = tar_temp 
        self.tar_time = tar_time 
        self.alarm = alarm

class DwellFrame(QtWidgets.QFrame):
    def __init__(self, obj: Dwell):
        super().__init__()

        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)

        

        self.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(40, 0))
        font = QtGui.QFont()
        font.setPointSize(21)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.frm_name = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(17)
        self.frm_name.setFont(font)
        self.frm_name.setObjectName("frm_name")
        self.horizontalLayout.addWidget(self.frm_name)
        self.frm_widget = QtWidgets.QWidget(self)
        self.frm_widget.setStyleSheet("background-color: transparent")
        self.frm_widget.setObjectName("frm_widget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frm_widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frm_widget_2 = QtWidgets.QWidget(self.frm_widget)
        self.frm_widget_2.setObjectName("frm_widget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frm_widget_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lineEdit = QtWidgets.QLineEdit(self.frm_widget_2)
        self.lineEdit.setStyleSheet("background-color: rgba(0,0,0,60)")
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setText(str(obj.tar_temp))
        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.frm_widget_2)
        self.lineEdit_2.setStyleSheet("background-color: rgba(0,0,0,60)")
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setText(str(obj.tar_time))
        self.horizontalLayout_2.addWidget(self.lineEdit_2)
        self.verticalLayout_3.addWidget(self.frm_widget_2)
        self.widget_4 = QtWidgets.QWidget(self.frm_widget)
        self.widget_4.setObjectName("widget_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_4)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.progressBar = QtWidgets.QProgressBar(self.widget_4)
        self.progressBar.setStyleSheet("background-color: rgba(0,0,0,60);\n"
"")
        self.progressBar.setProperty("value", 70)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout_3.addWidget(self.progressBar)
        self.lbl_rest_time = QtWidgets.QLabel(self.widget_4)
        self.lbl_rest_time.setObjectName("lbl_rest_time")
        self.horizontalLayout_3.addWidget(self.lbl_rest_time)
        self.verticalLayout_3.addWidget(self.widget_4)
        self.horizontalLayout.addWidget(self.frm_widget)
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setMinimumSize(QtCore.QSize(70, 70))
        self.pushButton.setStyleSheet("background-color: rgba(0,0,0,60); \n"
"border: none;\n"
"border-radius: 8px;")
        self.pushButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(f'../src/assets/alarm{"1" if obj.alarm else "0"}.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QtCore.QSize(50, 50))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self)
        font = QtGui.QFont()
        font.setPointSize(19)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setStyleSheet("background-color: transparent;\n"
"border: none;\n"
"")
        self.pushButton_2.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../src/assets/3-dots-gray.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_2.setIcon(icon1)
        self.pushButton_2.setIconSize(QtCore.QSize(30, 30))
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        # self.verticalLayout.addWidget(self)

        # Fill labels
        # name_label = QtWidgets.QLabel(obj.name)
        # name_label.setAlignment(Qt.AlignLeft)

        # value_label = QtWidgets.QLabel(str(obj.value))
        # value_label.setAlignment(Qt.AlignLeft)

        # layout.addWidget(name_label)
        # layout.addWidget(value_label)
