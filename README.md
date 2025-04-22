# brewery_heating_control
A brewery which consist of 3 pots (mash, fill, cook) should be analog heat controlled.

The temperature data is delivered by a digital sensor (DS18B20) which sends the values to an Arduino Mega 2560 Rev3.
It ist connected to a Raspberry Pi 4 via USB cable. This component does the calculating and 
sends the needed heating values back to the Arduino. The Arduino then controls the induction heating plates with 3 Bits.

These heating plates are HENDI Modell 3500 M with electic power values from 500W to 3500W in 100W steps.
They have self built in circuit boards which can decide if the plate should be controlled by the Arduino, 
if the plate should be on/off and with how much electric power the indution plates should heat.

## Get Started
### Installation
- To change the `.ui` use [Qt Creator 13.0.2](https://download.qt.io/official_releases/qtcreator/13.0/13.0.2/)
- `pip install PyQt5`
- `pip install pyqt5-tools`
- `pip install pyserial`

##### Create interface.py
``` bash
pyuic5 -x interface.ui -o interface.py
# -d for logs
```

### Possibly occuring errors
```
opening serial port: [Errno 13] could not open port /dev/ttyS0: [Errno 13] Permission denied: '/dev/ttyS0'
```
- Raspberry Pi couldn't connect to the Arduino
- **Possible problem:** Arduino is not connected with USB-cable

---
## Project History

This project has been in development since 2022.  
Prior to understanding version control with GitHub, versioning was managed using dated folders.  
The first version uploaded to GitHub was created on 11th March 2024.
