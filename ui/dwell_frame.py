from PyQt5 import QtCore, QtGui, QtWidgets
from selectalldoublespinbox import SelectAllDoubleSpinBox

dwell_names = [
    # TODO: Safe the Dwell Names and their min and max, temp and time as a "static" variable
    "Verzuckerungsrast", "Maltoserast", "Eiweißrast"
]

class Dwell:
    
    def __init__(self, tar_temp: float, tar_time:float, alarm: bool):
        self.tar_temp = tar_temp 
        self.tar_time = tar_time 
        self.alarm = alarm

    def getName(self):
        # TODO: Give all the Dwell Names and a effitient way to find the correct one. Else the name ist Rast
        return dwell_names[0]

    def toggleAlarm(self):
        self.alarm = not self.alarm

        

class DwellFrame(QtWidgets.QFrame):
    temp_changed = QtCore.pyqtSignal(int, float)
    time_changed = QtCore.pyqtSignal(int, float)
    up_clicked = QtCore.pyqtSignal(object)
    down_clicked = QtCore.pyqtSignal(object)
    new_clicked = QtCore.pyqtSignal(object)
    delete_clicked = QtCore.pyqtSignal(object)
    
    def __init__(self, index:int, obj: Dwell):
        super().__init__()
        self.index = index
        self.obj = obj
        self.locale = QtCore.QLocale(QtCore.QLocale.German, QtCore.QLocale.Germany)
        self.spinBox_font = QtGui.QFont()
        self.spinBox_font.setPointSize(16)

        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)

        self.setObjectName("frame")
        self.dwellLayout = QtWidgets.QHBoxLayout(self)
        self.dwellLayout.setSpacing(20)
        self.dwellLayout.setObjectName("dwellLayout")
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
        self.dwellLayout.addWidget(self.lbl_dwell_index)
        self.lbl_dwell_name = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(17)
        self.lbl_dwell_name.setFont(font)
        self.lbl_dwell_name.setObjectName("frm_name")
        self.lbl_dwell_name.setText(self.obj.getName())
        self.dwellLayout.addWidget(self.lbl_dwell_name)
        self.frm_widget = QtWidgets.QWidget(self)
        self.frm_widget.setStyleSheet("background-color: transparent")
        self.frm_widget.setObjectName("frm_widget")
        self.verticalDataLayout = QtWidgets.QVBoxLayout(self.frm_widget)
        self.verticalDataLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalDataLayout.setSpacing(0)
        self.verticalDataLayout.setObjectName("verticalDataLayout")
        self.frm_widget_2 = QtWidgets.QWidget(self.frm_widget)
        self.frm_widget_2.setObjectName("frm_widget_2")
        self.horizontalInputLayout = QtWidgets.QHBoxLayout(self.frm_widget_2)
        self.horizontalInputLayout.setObjectName("horizontalInputLayout")
        self.dsb_dwell_tar_temp = SelectAllDoubleSpinBox(self.frm_widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dsb_dwell_tar_temp.sizePolicy().hasHeightForWidth())
        self.dsb_dwell_tar_temp.setSizePolicy(sizePolicy)
        self.dsb_dwell_tar_temp.setMinimumSize(QtCore.QSize(120, 40))
        self.dsb_dwell_tar_temp.setFont(self.spinBox_font)
        self.dsb_dwell_tar_temp.setSuffix(" °C")
        self.dsb_dwell_tar_temp.setObjectName("dsb_dwell_tar_temp")
        self.dsb_dwell_tar_temp.setMinimum(0.0)
        self.dsb_dwell_tar_temp.setSpecialValueText(QtCore.QCoreApplication.translate("Form", "Dauer"))
        self.dsb_dwell_tar_temp.setValue(0.0 if self.obj.tar_temp is None else self.obj.tar_temp)
        #TODO: Maybe add a Focus all onclick (Not that easy)
        self.horizontalInputLayout.addWidget(self.dsb_dwell_tar_temp)
        self.dsb_dwell_tar_time = SelectAllDoubleSpinBox(self.frm_widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dsb_dwell_tar_time.sizePolicy().hasHeightForWidth())
        self.dsb_dwell_tar_time.setSizePolicy(sizePolicy)
        self.dsb_dwell_tar_time.setMinimumSize(QtCore.QSize(120, 40))
        self.dsb_dwell_tar_time.setFont(self.spinBox_font)
        self.dsb_dwell_tar_time.setSuffix(" min")
        self.dsb_dwell_tar_time.setObjectName("dsb_dwell_tar_time")
        self.dsb_dwell_tar_time.setMinimum(0.0)
        self.dsb_dwell_tar_time.setSpecialValueText(QtCore.QCoreApplication.translate("Form", "Temperatur"))
        self.dsb_dwell_tar_time.setValue(0.0 if self.obj.tar_time is None else self.obj.tar_time)
        #TODO: Maybe add a Focus all onclick (Not that easy)
        self.horizontalInputLayout.addWidget(self.dsb_dwell_tar_time)
        self.verticalDataLayout.addWidget(self.frm_widget_2)
        self.widget_4 = QtWidgets.QWidget(self.frm_widget)
        self.widget_4.setObjectName("widget_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_4)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.progressBar = QtWidgets.QProgressBar(self.widget_4)
        self.progressBar.setMaximumHeight(10)
        self.progressBar.setStyleSheet("background-color: rgba(255, 255, 255,60);\n"
"")
        self.progressBar.setProperty("value", 70)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName("progressBar")
        # TODO: Find a way to talk to the active dwell and update the progressBar
        # Popperbly with a pyqtSignal in the Timer (Look for the GPT Thread)
        self.horizontalLayout_3.addWidget(self.progressBar)
        self.lbl_dwell_rest_time = QtWidgets.QLabel(self.widget_4)
        self.lbl_dwell_rest_time.setObjectName("lbl_rest_time")
        self.lbl_dwell_rest_time.setText("4:32 min")
        self.horizontalLayout_3.addWidget(self.lbl_dwell_rest_time)
        self.verticalDataLayout.addWidget(self.widget_4)
        self.dwellLayout.addWidget(self.frm_widget)
        self.btn_dwell_alarm = QtWidgets.QPushButton(self)
        self.btn_dwell_alarm.setMinimumSize(QtCore.QSize(70, 70))
        self.btn_dwell_alarm.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_dwell_alarm.setStyleSheet("background-color: rgba(255, 255, 255,60); \n"
"border: none;\n"
"border-radius: 8px;")
        icon0 = QtGui.QIcon()
        icon0.addPixmap(QtGui.QPixmap(f'../src/assets/alarm0.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(f'../src/assets/alarm1.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ico_alarm = [icon0, icon1]

        self.btn_dwell_alarm.setIcon(self.ico_alarm[self.obj.alarm])
        self.btn_dwell_alarm.setIconSize(QtCore.QSize(50, 50))
        self.btn_dwell_alarm.setObjectName("btn_dwell_alarm")
        self.dwellLayout.addWidget(self.btn_dwell_alarm)
        self.btn_dwell_options = QtWidgets.QToolButton(self)
        self.btn_dwell_options.setStyleSheet("background-color: transparent;\n"
"border: none;\n"
"")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../src/assets/3-dots-gray.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_dwell_options.setIcon(icon1)
        self.btn_dwell_options.setIconSize(QtCore.QSize(30, 30))
        self.btn_dwell_options.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_dwell_options.setObjectName("btn_dwell_options")

        #region Connections
        self.dsb_dwell_tar_temp.textChanged.connect(self._on_temp_changed)
        self.dsb_dwell_tar_time.textChanged.connect(self._on_time_changed)
        self.btn_dwell_alarm.clicked.connect(self._on_alarm)

        # TODO: Make it more beautiful with icons in a own QFrame using QtCore.Qt.Popup and move it to the right location
        menu = QtWidgets.QMenu(self)
        font = menu.font()
        font.setPointSize(16)
        menu.setFont(font)
        act_up = QtWidgets.QAction("hoch", self)
        act_up.triggered.connect(self._on_dwell_up)
        act_down = QtWidgets.QAction("runter", self)
        act_down.triggered.connect(self._on_dwell_down)
        act_new = QtWidgets.QAction("neu", self)
        act_new.triggered.connect(self._on_new_dwell)
        act_delete = QtWidgets.QAction("löschen", self)
        act_delete.triggered.connect(self._on_delete_dwell)
        menu.addActions([act_up, act_down, act_new, act_delete])
        self.btn_dwell_options.setMenu(menu)
        self.btn_dwell_options.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.dwellLayout.addWidget(self.btn_dwell_options)

    def _on_temp_changed(self):
        self.temp_changed.emit(self.index, self.dsb_dwell_tar_temp.value())
        
    def _on_time_changed(self):
        self.time_changed.emit(self.index, self.dsb_dwell_tar_time.value())
        
    def _on_alarm(self):
        self.obj.toggleAlarm()
        print(f'Dwell {self.index} changes alarm to {self.obj.alarm}')
        self.btn_dwell_alarm.setIcon(self.ico_alarm[self.obj.alarm])

    def _on_dwell_up(self):
        self.up_clicked.emit(self.obj)

    def _on_dwell_down(self):
        self.down_clicked.emit(self.obj)

    def _on_new_dwell(self):
        self.new_clicked.emit(self.obj)
        
    def _on_delete_dwell(self):
        self.delete_clicked.emit(self.obj)