import sys, serial, logging, time
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel

class ThreadReadSer(QThread):

    def __init__(self, mash, fill, cook):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.info("ThreadReadSer initializing...")
        self.serial_port = serial.Serial('/dev/ttyS0', 9600, timeout=1)
        time.sleep(3)
        self.serial_port.reset_input_buffer()
        self.mash = mash
        self.fill = fill
        self.cook = cook
        self.running = True
        self.n_runs = 0 # counts temperature reading cycles
        self.logger.info("ThreadReadSer initialized successfully")

        self.previousSecs = 0.0
        self.interval = .5 # in s
            
    def run(self):
        self.logger.info("ThreadReadSer started - beginning serial communication")
        while self.running:
            ### WRITE #################################################################################################
            try:
                currentSecs = time.time()
                if (currentSecs - self.previousSecs >= self.interval):
                    self.previousSecs = currentSecs
                    
                    send = 0
                    mash_val = int(self.mash.heat_val / 440)
                    fill_val = int(self.fill.heat_val / 440)
                    cook_val = int(self.cook.heat_val / 440)
                    
                    if (self.mash.run_state == 3 or self.cook.run_state == 3):
                        send |= 512
                    
                    send |= (mash_val << 6)
                    send |= (fill_val << 3)
                    send |=  cook_val
                    #print(f"{bin(send|1024)}")
                    
                    toSend_str = str(send) + ';'
                    
                    self.serial_port.write(toSend_str.encode('utf-8'))
                    self.logger.debug(f"Sent to Arduino: {toSend_str} (mash:{mash_val}, fill:{fill_val}, cook:{cook_val})")
                    
            except Exception as e:
                self.logger.warning(f"Error writing serial data: {str(e)}")
                print(f"Error writing serial data: {str(e)}")
                
            ### READ ##################################################################################################
            try:
                data = self.serial_port.readline().decode().strip()
                
                if (data == ""):
                    self.logger.warning('Keine Sensordaten empfangen')
                    print('Keine Sensordaten empfangen')
                   
                if data:
                    parts = data.split(';')
            
                    if len(parts) == 4:
                        self.n_runs = 0
                        old_mash = self.mash.temp_now
                        old_fill = self.fill.temp_now
                        old_cook = self.cook.temp_now
                        
                        self.mash.temp_now = float(parts[0])
                        self.fill.temp_now = float(parts[1])
                        self.cook.temp_now = float(parts[2])
                        
                        # Log significant temperature changes
                        if (abs(old_mash - self.mash.temp_now) > 0.5 or 
                            abs(old_fill - self.fill.temp_now) > 0.5 or 
                            abs(old_cook - self.cook.temp_now) > 0.5):
                            self.logger.info(f"Temperature update - Mash:{self.mash.temp_now:.1f}°C, Fill:{self.fill.temp_now:.1f}°C, Cook:{self.cook.temp_now:.1f}°C")
                        
                        print(f'Read Arduino data: {parts[3]}')
                    else:
                        self.n_runs += 1
                        if self.n_runs >= 5:
                            self.n_runs = 0
                            error_msg = f'Thread hat für {5} Durchläufe, die Temperaturen nicht lesen können'
                            self.logger.error(error_msg)
                            raise RuntimeError(error_msg)

            except Exception as e:
                self.logger.warning(f"Error reading serial data: {str(e)}")
                print(f"Error reading serial data: {str(e)}")

    def stop(self):
        self.logger.info("ThreadReadSer stopping...")
        self.serial_port.write('0;'.encode("utf-8"))
        self.running = False
        self.logger.info("ThreadReadSer stopped")
        #self.serial_port.close()

#    def isRunning(self):
#        retung = self.running
