#! /usr/bin/python3.9
import cProfile
import sys, serial, logging, threading
sys.path.extend(["src"])#, "mockups"])

from time import gmtime, strftime, sleep
from datetime import datetime
from pathlib import Path
from PyQt5 import QtWidgets, QtGui, QtCore

now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
base_path = Path(__file__).resolve().parent
sys.path.append(str(base_path / 'mockups')) # TODO: Not shure why this is there

from components.pots.cook_pot import CookPot
from components.pots.dwell_pot import DwellPot
from components.pots.pots import Pot

from gui import interface, dwell_frame
from gui.styled_splash_screen import create_brewery_splash
from background_services.timer_heat_regulation import PeriodHeatReg
from background_services.timer_pot import PeriodTimePot
from background_services.thread_arduino import ThreadReadSer
from background_services.runtime_environment import DwellRuntimeEnvironment

DEBUG = True # TODO: Set false in production


def main():
    
    #region LOGGING
    log_path = base_path / 'logs' / f"{now}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(filename=log_path,
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d | %(message)s', 
                        filemode='a',
                        force=True
    )

    if DEBUG:
        # console output for debugging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d | %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Get the root logger and add console handler
        root_logger = logging.getLogger()
        root_logger.addHandler(console_handler)


    #region Import mockup
    try:
        from mockups.thread_mockup_ser import ThreadMockupSer
        logging.info("Successfully imported ThreadMockupSer")
    except ImportError as e:
        logging.error(f"Failed to import ThreadMockupSer: {e}")

        class ThreadMockupSer:
            def __init__(self, mash, fill, cook):
                # TODO: I think here has to be a logger
                self.mash = mash
                self.fill = fill
                self.cook = cook
                self.running = True
            def start(self):
                logging.info("Mock thread started")
            def stop(self):
                self.running = False

    serial_reader_thread = None
    

    #region ARDUINO INIT
    def _create_arduino_or_mockup_serial():
        global serial_reader_thread
        logging.info("Starting _create_arduino_or_mockup_serial()...")
        try:
            logging.info("Creating ThreadReadSer...")
            serial_reader_thread = ThreadReadSer(mash, fill, cook)
            logging.info("Initializing serial port...")
            serial_reader_thread.initialize_serial()  # Initialize serial port here
            logging.info("Starting serial thread...")
            serial_reader_thread.start()
            ui.lbl_connection_status.setText("Arduino ist verbunden")
            ui.lbl_connection_status.setStyleSheet("QLabel {background-color: darkgreen; color: lightgray; border-radius: 5;}")
            logging.info("Arduino successfully connected")
        except (serial.SerialException, PermissionError) as e:
            logging.error(f"Exception caught: {type(e).__name__}: {str(e)}")
            ui.lbl_connection_status.setText("Arduino nicht verbunden. Simulation läuft ...")
            ui.lbl_connection_status.setStyleSheet("QLabel {background-color: darkred; color: lightgray; border-radius: 5;}")
            serial_reader_thread = ThreadMockupSer(mash, fill, cook)
            serial_reader_thread.start()
            logging.error(f"opening serial port: {str(e)}")

    def connect2arduino():
        ui.lbl_connection_status.setText("Verbindungsversuch läuft...")
        ui.lbl_connection_status.setStyleSheet("QLabel {background-color: rgb(80, 80, 0); color: lightgray; border-radius: 5;}")
        QtWidgets.QApplication.processEvents()
        QtCore.QTimer.singleShot(1000, _create_arduino_or_mockup_serial)


    #region POTS
    mash = DwellPot('mash', DEBUG)
    fill = Pot('fill', DEBUG)
    cook = CookPot('cook', DEBUG) # TODO: Pot must be replaced with HopPot with multiple timers that alarm the brewer on certain times to the end of cooking


    #region INTERFACE
    app = QtWidgets.QApplication(sys.argv)


    #region LOAD IMAGES
    alarm0 = QtGui.QPixmap("src/assets/alarm0.png")
    alarm1 = QtGui.QPixmap("src/assets/alarm1.png")
    pot_white = QtGui.QPixmap("src/assets/pot_white.png")
#       pic_prop = QtGui.QPixmap("assets/propeller.png")
#       pic_pump = QtGui.QPixmap("assets/water-pump.png")

    # region SPLASH SCREEN
    splash = create_brewery_splash()
    splash.show()
    app.processEvents()  # Ensure the splash screen is displayed immediately
    
    MainWindow = QtWidgets.QMainWindow()
    ui = interface.Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    if not DEBUG:
        ui.tab_widget.removeTab(ui.tab_widget.indexOf(ui.tab_debug))
    
    # Look glitchy, because when starting the fixed size gets displayed for a short time
    # screen_rect = QtWidgets.QDesktopWidget().availableGeometry()
    # MainWindow.setGeometry(0, 0, screen_rect.width(), screen_rect.height())
    
    string_lbl_time_state = 'color: rgb(%s);border-radius: 4px;'
    colors_lbl_time_state = [
        '212, 212, 212',
        '255, 255, 100',
        '150, 255, 150',
        '255, 121, 121']
    

    # region SET IMAGES
#       # Old Path: /home/raspberry/FilesBrewery/assets
#       app.setWindowIcon(icon_brewery)
#       ui.lbl_alarm_sym.setPixmap(alarm0)
    ui.lbl_mash_switch.setPixmap(pot_white)
    ui.lbl_fill_switch.setPixmap(pot_white)
    ui.lbl_cook_switch.setPixmap(pot_white)
#       ui.lbl_prop_switch.setPixmap(pic_prop)
#       ui.lbl_pump_switch.setPixmap(pic_pump)

# # TODO: Set alarm icons in the dwells
    
    
    #region TIME POT PERIOD
    time_mash_thread = PeriodTimePot(mash)
    time_cook_thread = PeriodTimePot(cook)
    
    #region HEAT REGULATION PERIOD
    heat_regulate_thread = PeriodHeatReg(mash, fill, cook, time_mash_thread, time_cook_thread)
    heat_regulate_thread.start()
    
    #region RUNTIME ENVIRONMENT (Mash Process Control)
    mash_runtime = DwellRuntimeEnvironment(mash, time_mash_thread)
    
    #region UI CONNECT
    # The Connections and the refered Methods have to stay here.
    # Tested: 
    # - Use connect outside of main.py with mainThread
    # - Use the ui element outside of main.py with mainThread

    def mash_temp_changed(new_temp):
        ui.lbl_cur_temp_mash.setText(f'{new_temp :.2f} °C')
        ui.dbg_lbl_cur_temp_mash.setText(f'{new_temp :.2f} °C') # Shows mash temperature in debug tab
    mash.temp_now_changed.connect(mash_temp_changed) # connect
    
    def fill_temp_changed(new_temp):
        ui.lbl_cur_temp_fill.setText(f'{new_temp :.2f} °C')
        ui.dbg_lbl_cur_temp_fill.setText(f'{new_temp :.2f} °C') # Shows fill temperature in debug tab
    fill.temp_now_changed.connect(fill_temp_changed) # connect
    
    def cook_temp_changed(new_temp):
        ui.lbl_cur_temp_cook.setText(f'{new_temp :.2f} °C')
        ui.dbg_lbl_cur_temp_cook.setText(f'{new_temp :.2f} °C') # Shows cook temperature in debug tab
    cook.temp_now_changed.connect(cook_temp_changed) # connect
    

    def mash_heat_changed(new_temp):
        ui.lbl_heat_w_mash.setText(f'{new_temp * 3500 :4.0f} W')
    mash.heat_val_changed.connect(mash_heat_changed) # connect

    def fill_heat_changed(new_temp):
        ui.lbl_heat_w_fill.setText(f'{new_temp * 3500 :4.0f} W')
    fill.heat_val_changed.connect(fill_heat_changed) # connect

    def cook_heat_changed(new_temp):
        ui.lbl_heat_w_cook.setText(f'{new_temp * 3500 :4.0f} W')
    cook.heat_val_changed.connect(cook_heat_changed) # connect

    # region UI - TIMER
    def mash_run_state_changed(new_state):
        ui.frame_4.setStyleSheet(string_lbl_time_state %colors_lbl_time_state[new_state])
    mash.run_state_changed.connect(mash_run_state_changed) # Just for recolering
    
    # def cook_run_state_changed(new_state):
    #     ui.lbl_time_cook_state.setStyleSheet(string_lbl_time_state % colors_lbl_time_state[new_state])
    #     mash_or_cook_time_elapsed()
    # cook.run_state_changed.connect(cook_run_state_changed)
    # -----------------------------------------------------------------------------------------------------------------
    
    # def cook_time_changed(act_time):
    #     ui.lbl_time_cook.setText(strftime("%H:%M:%S", gmtime(act_time)) + f'.{int((act_time % 1) *10)}')
    # cook.act_time_changed.connect(cook_time_changed) # connect
    
    # region UI - DWELLS
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
            # Signal-Verbindung für Highlight des aktuellen Dwells
            mash.current_dwell_index_changed.connect(frame.on_current_dwell_changed)
            
            ui.dwell_layout.addWidget(frame)

        ui.dwell_layout.addStretch()
        
    def temp_changed_handler(index, value):
        if index == mash.current_dwell_index:
            mash.tar_temp = value  # Setter emittiert tar_temp_changed → Label update
        else:
            mash._dwell_array[index].tar_temp = value
        if index == mash.current_dwell_index:
            mash.temp_tar = value  # PID update

    def time_changed_handler(index, value):
        mash._dwell_array[index].tar_time_ds = int(value * 600)  # min → ds (min * 60s * 10)

    def up_clicked_handler(obj):
        update_steps(mash.dwell_up(obj))

    def down_clicked_handler(obj):
            update_steps(mash.dwell_down(obj))
        
    def new_clicked_handler(obj):
        update_steps(mash.dwell_new(obj))

    def delete_clicked_handler(obj):
        update_steps(mash.dwell_delete(obj))

    def on_dwell_progress(dwell_index, elapsed_ds, total_ds, remaining_ds):
        for i in range(ui.dwell_layout.count()):
            widget = ui.dwell_layout.itemAt(i).widget()
            if hasattr(widget, 'index') and widget.index == dwell_index:
                total_seconds = total_ds // 10
                remaining_seconds = remaining_ds // 10
                minutes = int(remaining_seconds // 60)
                seconds = int(remaining_seconds % 60)
                widget.update_progress(elapsed_ds, total_ds, f"{minutes}:{seconds:02d} min")

                ui.dbg_pgb_dwell_percentage.setMaximum(total_ds)
                ui.dbg_pgb_dwell_percentage.setValue(elapsed_ds)

    mash.dwell_progress_changed.connect(on_dwell_progress)

    def mash_start_clicked():
        """Startet/Fortsetzt die Mash-Prozess-Sequenz über die Runtime Environment"""
        mash_runtime.start_mash()

    ui.btn_start_mash.clicked.connect(mash_start_clicked)

    def mash_stop_clicked():
        if not mash_runtime.is_running:
            return
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setWindowTitle('Maischprozess stoppen')
        msg.setText('Möchtest du den Maischprozess wirklich stoppen?')
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if msg.exec() == QtWidgets.QMessageBox.Ok:
            mash_runtime.stop_mash()

    ui.btn_stop_mash.clicked.connect(mash_stop_clicked)

    def on_alarm_triggered(dwell_index):
        dwell_array = mash.get_dwell_array()
        dwell_name = dwell_array[dwell_index].getName(dwell_index, len(dwell_array))
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle('Rast abgelaufen')
        msg.setText(f'{dwell_name} (Dwell {dwell_index + 1}) ist abgelaufen.\nWeiter zum nächsten Schritt?')
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        if msg.exec() == QtWidgets.QMessageBox.Ok:
            mash_runtime.confirm_alarm()

    mash_runtime.alarm_triggered.connect(on_alarm_triggered)

    def update_tar_temp_label():
        if mash.current_dwell_index >= 0:
            dwell_array = mash.get_dwell_array()
            if mash.current_dwell_index < len(dwell_array):
                tar_temp = dwell_array[mash.current_dwell_index].tar_temp
                ui.lbl_tar_temp_mash.setText(f'{tar_temp} °C')
        else:
            ui.lbl_tar_temp_mash.setText('--°C')

    def on_current_dwell_index_changed(_):
        update_tar_temp_label()

    mash.current_dwell_index_changed.connect(on_current_dwell_index_changed)
    mash.tar_temp_changed.connect(on_current_dwell_index_changed)
    
    # -----------------------------------------------------------------------------------------------------------------
#       def mash_start_timer_state_shift():
#           if mash.run_state == 0:
#               mash.run_state = 1
#           elif mash.run_state == 2:
#               time_mash_thread.start()
#       ui.btn_start_mash.clicked.connect(mash_start_timer_state_shift) # connect
    
    def cook_start_timer_state_shift():
        if cook.run_state == 0:
            cook.run_state = 1
            # ui.lbl_connection_status.setText('button ist gedrückt')
        elif cook.run_state == 2:
            time_cook_thread.start()
            # ui.lbl_connection_status.setText('button wieder gedrückt')
    # ui.btn_start_cook.clicked.connect(cook_start_timer_state_shift) # connect #!!! DIESE NAMEN HIER NOCH ÄNDERN!!! DAS SIND KEINE CHECKABLE BUTTONS MEHR
    # -----------------------------------------------------------------------------------------------------------------
    def cook_pause_clicked():
        if cook.run_state == 1:
            cook.run_state = 0
        elif cook.run_state == 2:
            time_cook_thread.pause()
    ui.btn_pause_cook.clicked.connect(cook_pause_clicked) # connect
    # -----------------------------------------------------------------------------------------------------------------
#       def mash_act_time_changed():
#           if mash.run_state != 3:
#               try:
#                   mash.act_time = float(ui.lne_time_mash.text().replace(',','.')) * 60
#                   #print(f'Got mash.act_time = {mash.act_time/60}')
#               except ValueError as e:
#                   logging.error(f"ValueError occured from lne_time_mash: {str(e)}")
#                   print(f"ValueError occured from lne_time_mash: {str(e)}")
#                   mash.act_time = 0
#       ui.lne_time_mash.editingFinished.connect(mash_act_time_changed) # connect
    
    def cook_act_time_changed():
        if cook.run_state != 3:
            try:
                cook.rest_time_ds = int(float(ui.lne_time_cook.text().replace(',','.')) * 600)  # min → ds
                #print(f'Got .rest_time_ds = {cook.rest_time_ds}')
            except ValueError as e:
                logging.error(f"ValueError occured from lne_time_cook: {str(e)}")
                cook.rest_time_ds = 0
    ui.lne_time_cook.editingFinished.connect(cook_act_time_changed) # connect

    # --- TEMPERATURE -------------------------------------------------------------------------------------------------
    # Add Suffixes
    ui.dsb_fill_tar_temp.setSuffix(" °C")
    ui.dsb_cook_tar_temp.setSuffix(" °C")

    def fill_tar_temp_changed():
        try:
            fill.temp_tar = float(ui.dsb_fill_tar_temp.value())
            logging.info(f'Got fill.temp_tar = {fill.temp_tar}')
        except ValueError as e:
            logging.error(f"from lne_temp_fill returned {ui.lne_temp_fill}: {str(e)}")
            fill.temp_tar = 0
    ui.dsb_fill_tar_temp.valueChanged.connect(fill_tar_temp_changed) # connect

    def cook_tar_temp_changed():
        try:
            cook.temp_tar = float(ui.dsb_cook_tar_temp.value())
            logging.info(f'Got cook.temp_tar = {cook.temp_tar}')
        except ValueError as e:
            logging.error(f"lne_temp_cook returned {ui.lne_temp_cook}: {str(e)}")
            cook.temp_tar = 0
    ui.dsb_cook_tar_temp.valueChanged.connect(cook_tar_temp_changed) # connect


    # --- TEMPERATUR REGULATION ---------------------------------------------------------------------------------------
    def fill_heat_regulation_shift(): # button is checkable
        fill.heat_regulation = not fill.heat_regulation
        logging.info(f'Fill heat regulation {fill.heat_regulation}')
    ui.btn_heat_fill.clicked.connect(fill_heat_regulation_shift) # connect

    def cook_heat_regulation_shift(): # button is checkable
        cook.heat_regulation = not cook.heat_regulation
        logging.info(f'Cook heat regulation {cook.heat_regulation}')
    ui.btn_heat_cook.clicked.connect(cook_heat_regulation_shift) # connect

    # -----------------------------------------------------------------------------------------------------------------
    # TODO: !!! Hier sicherstellen das alles im Hintergrund funktioniert (Das die Threads laufen)

    # region UI - SETTINGS
    ui.btn_connect2arduino.clicked.connect(connect2arduino)


    # region UI - DEBUG TAB
    # --- TEMPERATURE OVERRIDE ----------------------------------------------------------------------------------------
    def override_cur_temp_mash():
        new_temp = ui.dbg_dsb_cur_temp_mash.value()
        if type(new_temp) == float and new_temp > 0:
            mash.temp_now = new_temp
    ui.dbg_btn_cur_temp_mash.clicked.connect(override_cur_temp_mash)

    def override_cur_temp_fill():
        new_temp = ui.dbg_dsb_cur_temp_fill.value()
        if type(new_temp) == float and new_temp > 0:
            fill.temp_now = new_temp
    ui.dbg_btn_cur_temp_fill.clicked.connect(override_cur_temp_fill)

    def override_cur_temp_cook():
        new_temp = ui.dbg_dsb_cur_temp_cook.value()
        if type(new_temp) == float and new_temp > 0:
            cook.temp_now = new_temp
    ui.dbg_btn_cur_temp_cook.clicked.connect(override_cur_temp_cook)

    # --- DWELL PERCENTAGE OVERRIDE ----------------------------------------------------------------------------------
    ui.dbg_dsb_dwell_percentage.setSuffix(" %") # Add Suffix
    
    def override_dwell_percentage():
        new_percentage = ui.dbg_dsb_dwell_percentage.value()
        if type(new_percentage) == float and new_percentage >= 0 and new_percentage <= 100:
            mash.set_rest_time_ds_percentage(new_percentage)
    ui.dbg_btn_dwell_percentage.clicked.connect(override_dwell_percentage)

        
    #region SHOW UI
    # Override closeEvent to show confirmation dialog
    def closeEvent(event):
        exit_msg = QtWidgets.QMessageBox()
        exit_msg.setIcon(QtWidgets.QMessageBox.Warning)
        exit_msg.setWindowTitle('WARNUNG!')
        exit_msg.setText('Programm wird geschlossen!')
        exit_msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

        return_value = exit_msg.exec()
        if return_value == 1024:  # Ok button
            # Close window immediately for better UX
            event.accept()
            
            # Stop threads in background
            def cleanup_threads():
                global serial_reader_thread
                heat_regulate_thread.stop()
                time_mash_thread.pause()
                time_cook_thread.pause()
                if serial_reader_thread is not None:
                    serial_reader_thread.stop()
                # Give threads a moment to finish
                sleep(0.5)
                sys.exit(0)
            
            # Start cleanup in background thread
            cleanup_thread = threading.Thread(target=cleanup_threads, daemon=True)
            cleanup_thread.start()
        else:
            event.ignore()  # Ignore the close event
    

    MainWindow.closeEvent = closeEvent
    splash.finish(MainWindow)
    MainWindow.show()
    # MainWindow.showMaximized() # Looks glitchy because MainWindow has a fixed size

    QtCore.QTimer.singleShot(100, connect2arduino)


    # TODO: I should clean up the dwells from the interface.ui or put some persistant stored dwells in there
    # clear_steps()
    update_steps(mash.get_dwell_array())
    
    # Start the application event loop
    sys.exit(app.exec_())


if DEBUG:
    cProfile.run('main()')
else:
    main()
    

#                      _
#                     : \
#                     ;\ \_                   _
#                     ;@: ~:              _,-;@)
#                     ;@: ;~:          _,' _,'@;
#                     ;@;  ;~;      ,-'  _,@@@,'
#                    |@(     ;      ) ,-'@@@-;
#                    ;@;   |~~(   _/ /@@@@@@/
#                    \@\   ; _/ _/ /@@@@@@;~
#                     \@\   /  / ,'@@@,-'~
#                       \\  (  ) :@@(~
#                    ___ )-'~~~~`--/ ___
#                   (   `--_    _,--'   )
#                  (~`- ___ \  / ___ -'~)
#                 __~\_(   \_~~_/   )_/~__
#              ,-'~~~~~`-._ 0\/0 _,-'~~~~~`-.
#             ;     ______ `----'  ______    :
#             ;    {      \   ~   /      }   |
#             `-._      ,-,' ~~  `.-.      _,'
#                 `----' ,'       `, `----'
#                        `-._/#\_,-'
#                           (###)
#                            `-'