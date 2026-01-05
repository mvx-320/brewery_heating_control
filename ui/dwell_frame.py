from PyQt5 import QtCore, QtGui, QtWidgets, Qt

dwell_names = [
    # TODO: Safe the Dwell Names and their min and max, temp and time as a "static" variable
    "Verzuckerungsrast", "Maltoserast", "Eiweißrast"
]

class Dwell:
    
    def __init__(self, tar_temp: int, tar_time:int, alarm: bool):
        self.tar_temp = tar_temp 
        self.tar_time = tar_time 
        self.alarm = alarm

    def getName(self):
        # TODO: Give all the Dwell Names and a effitient way to find the correct one. Else the name ist Rast
        return dwell_names[0]

        

class DwellFrame(QtWidgets.QFrame):
    def __init__(self, index:int, obj: Dwell):
        super().__init__()

        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)

        self.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lbl_dwell_index = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_dwell_index.sizePolicy().hasHeightForWidth())
        self.lbl_dwell_index.setSizePolicy(sizePolicy)
        self.lbl_dwell_index.setMinimumSize(QtCore.QSize(40, 0))
        font = QtGui.QFont()
        font.setPointSize(21)
        self.lbl_dwell_index.setFont(font)
        self.lbl_dwell_index.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_dwell_index.setObjectName("label")
        self.lbl_dwell_index.setText(f'{index +1}.')
        self.horizontalLayout.addWidget(self.lbl_dwell_index)
        self.lbl_dwell_name = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(17)
        self.lbl_dwell_name.setFont(font)
        self.lbl_dwell_name.setObjectName("frm_name")
        self.lbl_dwell_name.setText(obj.getName())
        self.horizontalLayout.addWidget(self.lbl_dwell_name)
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
        self.lne_dwell_tar_temp = QtWidgets.QLineEdit(self.frm_widget_2)
        self.lne_dwell_tar_temp.setStyleSheet("background-color: rgba(0,0,0,60)")
        self.lne_dwell_tar_temp.setAlignment(QtCore.Qt.AlignCenter)
        self.lne_dwell_tar_temp.setObjectName("lineEdit")
        self.lne_dwell_tar_temp.setText(str(obj.tar_temp))
        self.horizontalLayout_2.addWidget(self.lne_dwell_tar_temp)
        self.lne_dwell_tar_time = QtWidgets.QLineEdit(self.frm_widget_2)
        self.lne_dwell_tar_time.setStyleSheet("background-color: rgba(0,0,0,60)")
        self.lne_dwell_tar_time.setAlignment(QtCore.Qt.AlignCenter)
        self.lne_dwell_tar_time.setObjectName("lineEdit_2")
        self.lne_dwell_tar_time.setText(str(obj.tar_time))
        self.horizontalLayout_2.addWidget(self.lne_dwell_tar_time)
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
        self.lbl_dwell_rest_time = QtWidgets.QLabel(self.widget_4)
        self.lbl_dwell_rest_time.setObjectName("lbl_rest_time")
        self.lbl_dwell_rest_time.setText("4:32 min")
        self.horizontalLayout_3.addWidget(self.lbl_dwell_rest_time)
        self.verticalLayout_3.addWidget(self.widget_4)
        self.horizontalLayout.addWidget(self.frm_widget)
        self.btn_dwell_alarm = QtWidgets.QPushButton(self)
        self.btn_dwell_alarm.setMinimumSize(QtCore.QSize(70, 70))
        self.btn_dwell_alarm.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_dwell_alarm.setStyleSheet("background-color: rgba(0,0,0,60); \n"
"border: none;\n"
"border-radius: 8px;")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(f'../src/assets/alarm{"1" if obj.alarm else "0"}.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_dwell_alarm.setIcon(icon)
        self.btn_dwell_alarm.setIconSize(QtCore.QSize(50, 50))
        self.btn_dwell_alarm.setObjectName("btn_dwell_alarm")
        self.horizontalLayout.addWidget(self.btn_dwell_alarm)
        self.btn_dwell_options = QtWidgets.QPushButton(self)
        font = QtGui.QFont()
        font.setPointSize(19)
        self.btn_dwell_options.setFont(font)
        self.btn_dwell_options.setStyleSheet("background-color: transparent;\n"
"border: none;\n"
"")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../src/assets/3-dots-gray.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_dwell_options.setIcon(icon1)
        self.btn_dwell_options.setIconSize(QtCore.QSize(30, 30))
        self.btn_dwell_options.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_dwell_options.setObjectName("btn_dwell_options")
        self.horizontalLayout.addWidget(self.btn_dwell_options)