#! /usr/bin/python3.9

import sys, serial, logging
from time import gmtime, strftime
from PyQt5 import QtWidgets, QtGui

from pots import Pot, TimerPot
import interface
from periodic_classes import PeriodHeatReg, PeriodTimePot
from thread_read_ser import ThreadReadSer


if __name__ == "__main__":
    
    ### LOGGING #######################################################################################################
    logging.basicConfig(filename='zz_sensor_errors.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')
    logging.info('#################################### NEW START OF THE PROGRAM ####################################')

    ### POTS ##########################################################################################################
    mash = TimerPot('mash')
    fill = Pot('fill')
    cook = TimerPot('cook')

    ### INTERFACE #####################################################################################################
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = interface.Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    string_lbl_time_state = 'background: rgb(%s);border-radius: 4px;'
    colors_lbl_time_state = [
        '212, 212, 212',
        '255, 255, 100',
        '150, 255, 150',
        '255, 121, 121']
    
    ### LOAD IMAGES ###################################################################################################
    icon_brewery = QtGui.QIcon("/home/raspberry/FilesBrewery/assets/icon_brewery.png")
    alarm0 = QtGui.QPixmap("/home/raspberry/FilesBrewery/assets/alarm0.png")
    alarm1 = QtGui.QPixmap("/home/raspberry/FilesBrewery/assets/alarm1.png")
    pic_cook = QtGui.QPixmap("/home/raspberry/FilesBrewery/assets/cook.png")
    pic_prop = QtGui.QPixmap("/home/raspberry/FilesBrewery/assets/propeller.png")
    pic_pump = QtGui.QPixmap("/home/raspberry/FilesBrewery/assets/water-pump.png")
    app.setWindowIcon(icon_brewery)
    ui.lbl_alarm_sym.setPixmap(alarm0)
    ui.lbl_mash_switch.setPixmap(pic_cook)
    ui.lbl_fill_switch.setPixmap(pic_cook)
    ui.lbl_cook_switch.setPixmap(pic_cook)
    ui.lbl_prop_switch.setPixmap(pic_prop)
    ui.lbl_pump_switch.setPixmap(pic_pump)
    
    
    ### TIME POT PERIOD ###############################################################################################
    time_mash_thread = PeriodTimePot(mash)
    time_cook_thread = PeriodTimePot(cook)
    
    ### HEAT REGULATION PERIOD ########################################################################################
    heat_regulate_thread = PeriodHeatReg(mash, fill, cook, time_mash_thread, time_cook_thread)
    heat_regulate_thread.start()
    
    ### SERIAL READER THREAD ##########################################################################################
    serial_reader_thread = None

    def connect2serial():
        serial_reader_thread = ThreadReadSer(logging, mash, fill, cook)
        serial_reader_thread.start()


    for _ in range(3):
        try:
            connect2serial()
            break
        except serial.SerialException as e:
            logging.error(f'opening serial port: {str(e)}')
            print(f'opening serial port: {str(e)}')
    else:
        logging.error(
            'SERIAL-THREAD IS NOT ABLE TO START\tprogram will be stopped\tMögliche Ursache: Arduino nicht angeschlossen')
        print(
            'SERIAL-THREAD IS NOT ABLE TO START\tprogram will be stopped\n\nMögliche Ursache: Arduino nicht angeschlossen')
        logging.info(
            '######################################## PROGRAM  STOPPED ########################################')
        sys.exit(1)
       
    ### UI CONNECT #################################################################################################
    def mash_temp_changed(new_temp):
        ui.lbl_temp_mash.setText(f'{new_temp :.2f} °C')
    mash.temp_now_changed.connect(mash_temp_changed) # connect
    
    def fill_temp_changed(new_temp):
        ui.lbl_temp_fill.setText(f'{new_temp :.2f} °C')
    fill.temp_now_changed.connect(fill_temp_changed) # connect
    
    def cook_temp_changed(new_temp):
        ui.lbl_temp_cook.setText(f'{new_temp :.2f} °C')
    cook.temp_now_changed.connect(cook_temp_changed) # connect
    # -----------------------------------------------------------------------------------------------------------------
    def mash_heat_changed(new_temp):
        ui.lbl_heat_w_mash.setText(f'{new_temp :4.0f} W')
    mash.heat_val_changed.connect(mash_heat_changed) # connect

    def fill_heat_changed(new_temp):
        ui.lbl_heat_w_fill.setText(f'{new_temp :4.0f} W')
    fill.heat_val_changed.connect(fill_heat_changed) # connect

    def cook_heat_changed(new_temp):
        ui.lbl_heat_w_cook.setText(f'{new_temp :4.0f} W')
    cook.heat_val_changed.connect(cook_heat_changed) # connect
    # --- TIMER -------------------------------------------------------------------------------------------------------
    def mash_run_state_changed(new_state):
        ui.lbl_time_mash_state.setStyleSheet(string_lbl_time_state % colors_lbl_time_state[new_state])
        mash_or_cook_time_elapsed()
    mash.run_state_changed.connect(mash_run_state_changed)
    
    def cook_run_state_changed(new_state):
        ui.lbl_time_cook_state.setStyleSheet(string_lbl_time_state % colors_lbl_time_state[new_state])
        mash_or_cook_time_elapsed()
    cook.run_state_changed.connect(cook_run_state_changed)
    # -----------------------------------------------------------------------------------------------------------------
    def mash_time_changed(act_time):
        ui.lbl_time_mash.setText(strftime("%H:%M:%S", gmtime(act_time)) + f'.{int((act_time % 1) *10)}')
    mash.act_time_changed.connect(mash_time_changed) # connect
    
    def cook_time_changed(act_time):
        ui.lbl_time_cook.setText(strftime("%H:%M:%S", gmtime(act_time)) + f'.{int((act_time % 1) *10)}')
    cook.act_time_changed.connect(cook_time_changed) # connect
    # -----------------------------------------------------------------------------------------------------------------
    def mash_play_timer_state_shift():
        if mash.run_state == 0:
            mash.run_state = 1
        elif mash.run_state == 2:
            time_mash_thread.start()
    ui.btn_play_mash.clicked.connect(mash_play_timer_state_shift) # connect
    
    def cook_play_timer_state_shift():
        if cook.run_state == 0:
            cook.run_state = 1
        elif cook.run_state == 2:
            time_cook_thread.start()
    ui.btn_play_cook.clicked.connect(cook_play_timer_state_shift) # connect #!!! DIESE NAMEN HIER NOCH ÄNDERN!!! DAS SIND KEINE CHECKABLE BUTTONS MEHR
    # -----------------------------------------------------------------------------------------------------------------
    def mash_pause_clicked():
        if mash.run_state == 1:
            mash.run_state = 0
        elif mash.run_state == 2:
            time_mash_thread.pause()
    ui.btn_pause_mash.clicked.connect(mash_pause_clicked) # connect
    
    def cook_pause_clicked():
        if cook.run_state == 1:
            cook.run_state = 0
        elif cook.run_state == 2:
            time_cook_thread.pause()
    ui.btn_pause_cook.clicked.connect(cook_pause_clicked) # connect
    # -----------------------------------------------------------------------------------------------------------------
    def mash_act_time_changed():
        if mash.run_state != 3:
            try:
                mash.act_time = float(ui.lne_time_mash.text().replace(',','.')) * 60
                #print(f'Got mash.act_time = {mash.act_time/60}')
            except ValueError as e:
                logging.error(f"ValueError occured from lne_time_mash: {str(e)}")
                print(f"ValueError occured from lne_time_mash: {str(e)}")
                mash.act_time = 0
    ui.lne_time_mash.editingFinished.connect(mash_act_time_changed) # connect
    
    def cook_act_time_changed():
        if cook.run_state != 3:
            try:
                cook.act_time = float(ui.lne_time_cook.text().replace(',','.')) * 60
                #print(f'Got cook.act_time = {cook.act_time/60}')
            except ValueError as e:
                logging.error(f"ValueError occured from lne_time_cook: {str(e)}")
                print(f"ValueError occured from lne_time_cook: {str(e)}")
                cook.act_time = 0
    ui.lne_time_cook.editingFinished.connect(cook_act_time_changed) # connect
    # --- TEMPERATURE -------------------------------------------------------------------------------------------------
    def mash_tar_temp_changed():
        try:
            mash.temp_tar = float(ui.lne_temp_mash.text().replace(',','.'))
            print(f'Got mash.temp_tar = {mash.temp_tar}')
        except ValueError as e:
            print(f"Wrong value got from lne_temp_mash: {str(e)}")
            mash.temp_tar = 0
    ui.lne_temp_mash.textChanged.connect(mash_tar_temp_changed) # connect

    def fill_tar_temp_changed():
        try:
            fill.temp_tar = float(ui.lne_temp_fill.text().replace(',','.'))
            print(f'Got fill.temp_tar = {fill.temp_tar}')
        except ValueError as e:
            print(f"Wrong value got from lne_temp_fill: {str(e)}")
            fill.temp_tar = 0
    ui.lne_temp_fill.textChanged.connect(fill_tar_temp_changed) # connect

    def cook_tar_temp_changed():
        try:
            cook.temp_tar = float(ui.lne_temp_cook.text().replace(',','.'))
            print(f'Got cook.temp_tar = {cook.temp_tar}')
        except ValueError as e:
            print(f"Wrong value got from lne_temp_cook: {str(e)}")
            cook.temp_tar = 0
    ui.lne_temp_cook.textChanged.connect(cook_tar_temp_changed) # connect
    # -----------------------------------------------------------------------------------------------------------------
    def mash_heat_regulation_shift(): # button is checkable
        mash.heat_regulation = not mash.heat_regulation
        print(mash.heat_regulation)
    ui.btn_heat_mash.clicked.connect(mash_heat_regulation_shift) # connect

    def fill_heat_regulation_shift(): # button is checkable
        fill.heat_regulation = not fill.heat_regulation
        print(fill.heat_regulation)
    ui.btn_heat_fill.clicked.connect(fill_heat_regulation_shift) # connect

    def cook_heat_regulation_shift(): # button is checkable
        cook.heat_regulation = not cook.heat_regulation
        print(cook.heat_regulation)
    ui.btn_heat_cook.clicked.connect(cook_heat_regulation_shift) # connect
    # --- ALARM -------------------------------------------------------------------------------------------------------
    def mash_or_cook_time_elapsed():
        if (mash.run_state == 3 or cook.run_state == 3):
            ui.lbl_alarm_sym.setPixmap(alarm1)
        else:
            ui.lbl_alarm_sym.setPixmap(alarm0)
    # -----------------------------------------------------------------------------------------------------------------
    def every_alarm_out():
        try:
            if mash.act_time < 0.0:
                time_mash_thread.pause()
                try:
                    new_time = float(ui.lne_time_mash.text().replace(',','.'))
                except:
                    new_time = 0
                mash.act_time =  new_time * 60
                mash.run_state = 0
                print('mash.run_state = 0')
            
            if cook.act_time < 0.0:
                time_cook_thread.pause()
                try:
                    new_time = float(ui.lne_time_cook.text().replace(',','.'))
                except:
                    new_time = 0
                cook.act_time =  new_time * 60
                cook.run_state = 0
                print('cook.run_state = 0')
                
            ui.lbl_alarm_sym.setPixmap(alarm0) # sollte eigentlich unnötig sein
        except Exception as e:
            print(f"Exception occured wenn transfer time values to the interface: {str(e)}")
    ui.btn_alarm_out.clicked.connect(every_alarm_out)
        
    # !!! Hier sicherstellen das alles im Hintergrund funktioniert (Das die Threads laufen)
    
    ### SHOWS UI ######################################################################################################
    while True:
        MainWindow.show()
        
        app.exec_()
        MainWindow.show()
        
        exit_msg = QtWidgets.QMessageBox()
        exit_msg.setIcon(QtWidgets.QMessageBox.Warning)
        exit_msg.setWindowTitle('WARNUNG!')
        exit_msg.setText('Programm wird geschlossen!')
        exit_msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

        return_value = exit_msg.exec()
        #print(str(return_value))
        if return_value == 1024:
            logging.info('######################################## PROGRAM FINISHED ########################################')
            heat_regulate_thread.stop()
            time_mash_thread.pause()
            time_cook_thread.pause()
            serial_reader_thread.stop()
            sys.exit(0)
