#! /usr/bin/python3.12
# Only necessary if brewing system calls programm with ./main.py

import cProfile
import sys, serial, logging, threading

from time import gmtime, strftime, sleep
from datetime import datetime
from pathlib import Path
from PyQt5 import QtWidgets, QtGui, QtCore

now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
base_path = Path(__file__).resolve().parent

from src.components.enums.pot_type import PotType
from src.components.enums.dwell_state import DwellState
from src.components.pots.cook_pot import CookPot
from src.components.pots.pot import Pot

from src.gui.splash_screen import create_brewery_splash
from src.gui.interface import Ui_MainWindow
from src.gui.dwell_signals import DwellSignals
from src.gui.dwell_frame import DwellFrame

from src.runtime.period_dwell_controller import PeriodDwellController
from src.runtime.timer_heat_regulation import PeriodHeatReg
from src.runtime.timer_pot import PeriodTimePot
from src.runtime.driver_serial import DriverSerial
from src.controls.dwell_controller import DwellController
from src.controls.pid_controller import PidController

# TODO: Remove when DwellPresenter comes
from src.dtos.dwell_events import \
    HeatValChangedEvent, \
    DwellStateChangedEvent, \
    DwellArrayChangedEvent, \
    DwellProgressChangedEvent, \
    AlarmToggledEvent, \
    DwellAdvancedEvent, \
    AllDwellsFinishedEvent

from simulation.driver_simulation import DriverSimulation

from src.gui.splash_screen import create_brewery_splash
SIMULATION = True # TODO: Set False in production
C_PROFILE = False # Set False in production. Get performance profile. 

driver_thread = None # Gets real serial thread or simulation

string_styleSheet_coloring = 'color: rgb(%s);border-radius: 4px;'
# colors keys are dwell_state.name.lower() -> cannot be changed
colors = {
    'idle':'212, 212, 212',
    'waiting': '255, 255, 100',
    'pending': '150, 255, 150',
    'alarm': '255, 121, 121'}

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

    if SIMULATION:
        # console output for simulation
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d | %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Get the root logger and add console handler
        root_logger = logging.getLogger()
        root_logger.addHandler(console_handler)


    #region Serial | Simulation
    def _create_brewery_connection():
        global driver_thread
        if driver_thread is not None:
            driver_thread.stop()
            driver_thread = None
        logging.info("Starting _create_brewery_connection()...")
        try:
            logging.info("Creating DriverSerial...")
            driver_thread = DriverSerial(mash, fill, cook)
            logging.info("Initializing serial port...")
            driver_thread.initialize_serial()  # Initialize serial port here
            logging.info("Starting serial thread...")
            driver_thread.start()
            ui.lbl_connection_status.setText("Brauerei ist verbunden")
            ui.lbl_connection_status.setStyleSheet("QLabel {background-color: darkgreen; color: lightgray; border-radius: 5;}")
            logging.info("Serial connection successful")
        except (serial.SerialException, PermissionError) as e:
            logging.error(f"Exception caught: {type(e).__name__}: {str(e)}")

            driver_thread = DriverSimulation(mash, fill, cook)
            driver_thread.start()

            driver_thread.sim_engine.time_s_changed.connect(on_time_s_changed)

            ui.lbl_connection_status.setText("Brauerei nicht verbunden. Simulation läuft ...")
            ui.lbl_connection_status.setStyleSheet("QLabel {background-color: darkred; color: lightgray; border-radius: 5;}")

    def connect_serial_device():
        ui.lbl_connection_status.setText("Verbindungsversuch läuft...")
        ui.lbl_connection_status.setStyleSheet("QLabel {background-color: rgb(80, 80, 0); color: lightgray; border-radius: 5;}")
        QtWidgets.QApplication.processEvents()
        QtCore.QTimer.singleShot(1000, _create_brewery_connection)
    #endregion Serial | Simulation


    #region POTS
    mash = Pot(PotType.MASH) # TODO: Use normal Pot
    fill = Pot(PotType.FILL)
    cook = CookPot(PotType.COOK)  # TODO: Use normal Pot


    #region INTERFACE
    app = QtWidgets.QApplication(sys.argv)


    #region LOAD IMAGES
    pot_white = QtGui.QPixmap("src/assets/pot_white.png")

    # region SPLASH SCREEN
    splash = create_brewery_splash()
    splash.show()
    app.processEvents()  # Ensure the splash screen is displayed immediately
    
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    if not SIMULATION:
        ui.tab_widget.removeTab(ui.tab_widget.indexOf(ui.tab_simulation))
    
    # Open in full screen look glitchy, because when starting the fixed size gets displayed for a short time
    # screen_rect = QtWidgets.QDesktopWidget().availableGeometry()
    # MainWindow.setGeometry(0, 0, screen_rect.width(), screen_rect.height())
    
    

    # region Set Images
#       # Old Path: /home/raspberry/FilesBrewery/assets
#       app.setWindowIcon(icon_brewery)
    ui.lbl_mash_switch.setPixmap(pot_white)
    ui.lbl_fill_switch.setPixmap(pot_white)
    ui.lbl_cook_switch.setPixmap(pot_white)

    
    #region Drivers, Controllers
    dwell_controller = DwellController(mash.pot_type)
    pid_controller = PidController(mash.pot_type)
    period_dwell_controller = PeriodDwellController(mash, dwell_controller, pid_controller)
    period_dwell_controller.start()  # Start the periodic dwell controller thread
    ##region TIME POT PERIOD
    time_cook_thread = PeriodTimePot(cook)
    
    ##region HEAT REGULATION PERIOD
    heat_regulate_thread = PeriodHeatReg(mash, fill, cook, time_cook_thread) # TODO: 1st Remove mash✅, later remove all completely
    heat_regulate_thread.start()
    
    
    
    #region UI CONNECT
    # The Connections and the refered Methods have to stay here.
    # Tested: 
    # - Use connect outside of main.py with mainThread
    # - Use the ui element outside of main.py with mainThread

    def mash_temp_changed(new_temp):
        ui.lbl_cur_temp_mash.setText(f'{new_temp :.2f} °C')
        ui.dbg_lbl_cur_temp_mash.setText(f'{new_temp :.2f} °C') # Shows mash temperature in simulation tab
    mash.temp_now_changed.connect(mash_temp_changed) # connect
    
    def fill_temp_changed(new_temp):
        ui.lbl_cur_temp_fill.setText(f'{new_temp :.2f} °C')
        ui.dbg_lbl_cur_temp_fill.setText(f'{new_temp :.2f} °C') # Shows fill temperature in simulation tab
    fill.temp_now_changed.connect(fill_temp_changed) # connect
    
    def cook_temp_changed(new_temp):
        ui.lbl_cur_temp_cook.setText(f'{new_temp :.2f} °C')
        ui.dbg_lbl_cur_temp_cook.setText(f'{new_temp :.2f} °C') # Shows cook temperature in simulation tab
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
    def dwell_state_changed(new_state):
        ui.frame_4.setStyleSheet(string_styleSheet_coloring %colors[new_state.name.lower()])

    def cook_state_changed(new_state):
        ui.frame_5.setStyleSheet(string_styleSheet_coloring %colors[new_state.name.lower()])
    # -----------------------------------------------------------------------------------------------------------------
    
    # def cook_time_changed(act_time):
    #     ui.lbl_time_cook.setText(strftime("%H:%M:%S", gmtime(act_time)) + f'.{int((act_time % 1) *10)}')
    # cook.act_time_changed.connect(cook_time_changed) # connect
    
    # region UI - DWELLS
    dwell_signals = DwellSignals() # HACK: Either move later to DwellPresenter or rebuild update_dwells()

    def _handle_events(events: list): # TODO: Move to DwellPresenter
        logging.info(f"Handling {len(events)} events: {[type(event).__name__ for event in events]}")
        for event in events:
            if isinstance(event, HeatValChangedEvent):
                mash.heat_val = event.heat_val

            elif isinstance(event, DwellStateChangedEvent):
                dwell_state_changed(event.new_state)

            elif isinstance(event, DwellArrayChangedEvent):
                # update_tar_temp_label(event.new_tar_temp) # Update tar_temp_label
                update_dwells(event.dwell_array)

            elif isinstance(event, DwellProgressChangedEvent):
                logging.info(f"Dwell progress changed: dwell_index={event.dwell_index}, rest_time_s={event.rest_time_s}, total_time_s={event.total_time_s}")
                on_dwell_progress(event.dwell_index, event.rest_time_s, event.total_time_s)

            elif isinstance(event, AlarmToggledEvent):
                mash.alarm_active = event.alarm_active
                if event.alarm_active:
                    on_alarm_triggered(event.dwell_index)

            elif isinstance(event, DwellAdvancedEvent):
                logging.info(f"Current dwell index changed to {event.dwell_index}, new target temperature: {event.new_tar_temp}")
                update_tar_temp_label(event.new_tar_temp)
                dwell_signals.dwell_advanced.emit(event.dwell_index)

            elif isinstance(event, AllDwellsFinishedEvent):
                pass

    period_dwell_controller.events_ready.connect(_handle_events)


    def clear_steps():
        layout = ui.dwell_layout
        
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def update_dwells(dwell_array):
        scroll = ui.steps_scroll.verticalScrollBar()
        print(f'Scroll-Value: {scroll.value()}')
        clear_steps()
        
        dwell_amount = len(dwell_array)
        for i, obj in enumerate(dwell_array):

            frame = DwellFrame(i, dwell_amount, obj) 

            frame.temp_changed.connect(temp_changed_handler)
            frame.time_changed.connect(time_changed_handler)
            frame.up_clicked.connect(up_clicked_handler)
            frame.down_clicked.connect(down_clicked_handler)
            frame.new_clicked.connect(new_clicked_handler)
            frame.delete_clicked.connect(delete_clicked_handler)
            dwell_signals.dwell_advanced.connect(frame.on_current_dwell_changed)
            
            ui.dwell_layout.addWidget(frame)

        ui.dwell_layout.addStretch()
        
    def temp_changed_handler(index, value):
        dwell_controller.set_dwell_temp(index, value) # TODO: Maybe trigger event
        update_tar_temp_label(dwell_controller.tar_temp) # TODO: Check if this needs change bcs not over central source 

    def time_changed_handler(index, value):
        dwell_controller.set_dwell_time(index, int(value * 60)) # min → s

    def up_clicked_handler(obj):
        events = dwell_controller.dwell_up(obj)
        if isinstance(events[0], DwellArrayChangedEvent):
            update_dwells(events[0].dwell_array)
        else:
            logging.error(f"Unexpected event type returned from dwell_up: {type(events[0]).__name__}")
        dwell_signals.dwell_advanced.emit(dwell_controller.current_dwell_index)
        return events

    def down_clicked_handler(obj): #TODO: Fix the others also
        events = dwell_controller.dwell_down(obj)
        if isinstance(events[0], DwellArrayChangedEvent):
            update_dwells(events[0].dwell_array)
        else:
            logging.error(f"Unexpected event type returned from dwell_down: {type(events[0]).__name__}")
        dwell_signals.dwell_advanced.emit(dwell_controller.current_dwell_index)
        return events 

    def new_clicked_handler(obj):
        events = dwell_controller.dwell_new(obj)
        if isinstance(events[0], DwellArrayChangedEvent):
            update_dwells(events[0].dwell_array)
        else:
            logging.error(f"Unexpected event type returned from dwell_new: {type(events[0]).__name__}")
        dwell_signals.dwell_advanced.emit(dwell_controller.current_dwell_index)
        return events

    def delete_clicked_handler(obj):
        events = dwell_controller.dwell_delete(obj)
        if isinstance(events[0], DwellArrayChangedEvent):
            update_dwells(events[0].dwell_array)
        else:
            logging.error(f"Unexpected event type returned from dwell_delete: {type(events[0]).__name__}")
        dwell_signals.dwell_advanced.emit(dwell_controller.current_dwell_index)
        return events

    def on_dwell_progress(dwell_index, rest_s, total_s): # TODO: Add interpolation in ds for UX
        if (total_s is None) or (rest_s is None):
            # logging.warning(f"on_dwell_progress called with None values: dwell_index={dwell_index}, rest_s={rest_s}, total_s={total_s}")
            return
        
        for i in range(ui.dwell_layout.count()):
            widget = ui.dwell_layout.itemAt(i).widget()
            if hasattr(widget, 'index') and widget.index == dwell_index:
                elapsed_s = total_s - rest_s
                minutes = int(rest_s // 60)
                seconds = int(rest_s % 60)
                widget.update_progress(elapsed_s, total_s, f"{minutes}:{seconds:02d} min")

                ui.dbg_pgb_dwell_percentage.setMaximum(total_s)
                ui.dbg_pgb_dwell_percentage.setValue(elapsed_s)


    def mash_start_clicked():
        logging.info("Starting mash process...")
        events = dwell_controller.start_mash()
        period_dwell_controller.events_ready.emit(events) 
    ui.btn_start_mash.clicked.connect(mash_start_clicked)

    def mash_stop_clicked():
        if not dwell_controller != DwellState.IDLE:
            return
        msg = QtWidgets.QMessageBox()
        # These 2 lines are to hold msg on top of all windows
        msg.setWindowModality(QtCore.Qt.ApplicationModal)
        msg.setWindowFlags(msg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setWindowTitle('Maischprozess stoppen')
        msg.setText('Möchtest du den Maischprozess wirklich stoppen?')
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if msg.exec() == QtWidgets.QMessageBox.Ok:
            events = dwell_controller.stop_mash()
            period_dwell_controller.events_ready.emit(events) # TODO: Error while stopping mash

    ui.btn_stop_mash.clicked.connect(mash_stop_clicked)

    def on_alarm_triggered(dwell_index):
        dwell_array = dwell_controller.dwell_array
        dwell_name = dwell_array[dwell_index].getName(dwell_index, len(dwell_array))
        msg = QtWidgets.QMessageBox()
        # These 2 lines are to hold msg on top of all windows
        msg.setWindowModality(QtCore.Qt.ApplicationModal)
        msg.setWindowFlags(msg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle('Rast abgelaufen')
        msg.setText(f'{dwell_name} (Rast {dwell_index + 1}) ist abgelaufen.\nWeiter zum nächsten Schritt?')
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        if msg.exec() == QtWidgets.QMessageBox.Ok:
            events = dwell_controller.confirm_alarm()
            period_dwell_controller.events_ready.emit(events)


    def update_tar_temp_label(tar_temp : float): # TODO: Called from handle_events 
        if (tar_temp is not None and tar_temp >= 0):
            # dwell_array = dwell_controller.get_dwell_array()
            # if mash.current_dwell_index < len(dwell_array):
                # tar_temp = dwell_array[mash.current_dwell_index].tar_temp
            ui.lbl_tar_temp_mash.setText(f'{tar_temp} °C')
        else:
            ui.lbl_tar_temp_mash.setText('--°C')

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
    ui.btn_connect_serial.clicked.connect(connect_serial_device)


    # region UI - SIMULATION TAB
    # --- TEMPERATURE OVERRIDE ----------------------------------------------------------------------------------------
    def override_cur_temp_mash():
        new_temp = ui.dbg_dsb_cur_temp_mash.value()
        if SIMULATION and type(new_temp) == float and new_temp > 0:
            global driver_thread
            driver_thread.sim_engine.thermal_systems[PotType.MASH].state.override(new_temp)
    ui.dbg_btn_cur_temp_mash.clicked.connect(override_cur_temp_mash)

    def override_cur_temp_fill():
        new_temp = ui.dbg_dsb_cur_temp_fill.value()
        if SIMULATION and type(new_temp) == float and new_temp > 0:
            global driver_thread
            driver_thread.sim_engine.thermal_systems[PotType.FILL].state.override(new_temp)
    ui.dbg_btn_cur_temp_fill.clicked.connect(override_cur_temp_fill)

    def override_cur_temp_cook():
        new_temp = ui.dbg_dsb_cur_temp_cook.value()
        if SIMULATION and type(new_temp) == float and new_temp > 0:
            global driver_thread
            driver_thread.sim_engine.thermal_systems[PotType.COOK].state.override(new_temp)
    ui.dbg_btn_cur_temp_cook.clicked.connect(override_cur_temp_cook)

    # --- TIME OVERRIDE ----------------------------------------------------------------------------------------------
    def on_time_s_changed(time_s):
        h = int(time_s // 3600)
        m = int((time_s % 3600)//60)
        s = int(time_s % 60)
        ui.dbg_lbl_time_s.setText(f'{h:02d}:{m:02d}:{s:02d}')
    # connect is in _create_brewery_connection()

    def override_time_plus_01min():
        driver_thread.pause()
        for _ in range(60):
            driver_thread.sim_engine.step_seconds(1)
            events = dwell_controller.tick(mash.temp_now)
            _handle_events(events)
        driver_thread.resume()
    ui.dbg_btn_plus_01min.clicked.connect(override_time_plus_01min)

    def override_time_plus_05min():
        driver_thread.pause()
        for _ in range(300):
            driver_thread.sim_engine.step_seconds(1)
            events = dwell_controller.tick(mash.temp_now)
            _handle_events(events)
        driver_thread.resume()
    ui.dbg_btn_plus_05min.clicked.connect(override_time_plus_05min)

    def override_time_plus_15min():
        driver_thread.pause()
        for _ in range(900):
            driver_thread.sim_engine.step_seconds(1)
            events = dwell_controller.tick(mash.temp_now)
            _handle_events(events)
        driver_thread.resume()
    ui.dbg_btn_plus_15min.clicked.connect(override_time_plus_15min)

    #region SHOW UI
    # Override closeEvent to show confirmation dialog
    def closeEvent(event):
        exit_msg = QtWidgets.QMessageBox()
        # These 2 lines are to hold msg on top of all windows
        exit_msg.setWindowModality(QtCore.Qt.ApplicationModal)
        exit_msg.setWindowFlags(exit_msg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        exit_msg.setIcon(QtWidgets.QMessageBox.Warning)
        exit_msg.setWindowTitle('WARNUNG!')
        exit_msg.setText('Programm wird geschlossen!')
        exit_msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

        return_value = exit_msg.exec()
        if return_value == 1024:  # Ok button
            # Close window immediately for better UX
            event.accept()
            
            # Stop threads in background
            # def cleanup_threads():
            #     global driver_thread

            heat_regulate_thread.stop()
            logging.info("Stopped heat_regulate_thread")
            # time_mash_thread.stop()
            period_dwell_controller.stop()
            logging.info("Stopped period_dwell_controller")
            time_cook_thread.stop()
            logging.info("Stopped time_cook_thread")
            if driver_thread is not None:
                driver_thread.stop()
            logging.info("Stopped driver_thread")
            # Give threads a moment to finish
            # sleep(0.5)
            sys.exit(0)
            
            # Start cleanup in background thread
            # cleanup_thread = threading.Thread(target=cleanup_threads, daemon=True)
            # cleanup_thread.start()
        else:
            event.ignore()  # Ignore the close event
    

    MainWindow.closeEvent = closeEvent
    splash.finish(MainWindow)
    MainWindow.show()
    # MainWindow.showMaximized() # Looks glitchy because MainWindow has a fixed size

    QtCore.QTimer.singleShot(100, connect_serial_device)


    # TODO: I should clean up the dwells from the interface.ui or put some persistant stored dwells in there
    # clear_steps()
    update_dwells(dwell_controller.dwell_array) # TODO: Should be called in the handle_events function
    
    # Start the application event loop
    sys.exit(app.exec_())


if C_PROFILE:
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