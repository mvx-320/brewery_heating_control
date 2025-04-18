
import serial, time
from PyQt5.QtCore import QThread


class ThreadReadSer(QThread):

    def __init__(self, logging, mash, fill, cook):
        super().__init__()
        self.logging = logging
        self.serial_port = serial.Serial('/dev/ttyS0', 9600, timeout=1)
        time.sleep(3)
        self.serial_port.reset_input_buffer()
        self.mash = mash
        self.fill = fill
        self.cook = cook
        self.running = True
        self.n_runs = 0 # counts temperature reading cycles

        self.previousSecs = 0.0
        self.interval = .5 # in s
            
    def run(self):
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
                    
            except Exception as e:
                self.logging.warning(f"Error writing serial data: {str(e)}")
                print(f"Error writing serial data: {str(e)}")
                
            ### READ ##################################################################################################
            try:
                data = self.serial_port.readline().decode().strip()
                
                if (data == ""):
                    self.logging.warning('Keine Sensordaten empfangen')
                    print('Keine Sensordaten empfangen')
                   
                if data:
                    parts = data.split(';')
            
                    if len(parts) == 4:
                        self.n_runs = 0
                        self.mash.temp_now = float(parts[0])
                        self.fill.temp_now = float(parts[1])
                        self.cook.temp_now = float(parts[2])
                        print(parts[3])
                    else:
                        self.n_runs += 1
                        if self.n_runs >= 5:
                            self.n_runs = 0
                            raise RuntimeError(f'Thread hat für {5} Durchläufe, die Temperaturen nicht lesen können')

            except Exception as e:
                self.logging.warning(f"Error reading serial data: {str(e)}")
                print(f"Error reading serial data: {str(e)}")

    def stop(self):
        self.serial_port.write('0;'.encode("utf-8"))
        self.running = False
        
        #self.serial_port.close()
