# brewery_heating_control
A brewery which consist of 3 pots (mash, fill, cook) should be analog heat controlled.

The temperature data is delivered by a digital sensor (DS18B20) which sends the values to an Arduino Mega 2560 Rev3.
It ist connected to a Raspberry Pi 4 via USB cable. This component does the calculating and 
sends the needed heating values back to the Arduino. The Arduino then controls the induction heating plates with 3 Bits.

These heating plates are HENDI Modell 3500 M with electic power values from 500W to 3500W in 100W steps.
They have self built in circuit boards which can decide if the plate should be controlled by the Arduino, 
if the plate should be on/off and with how much electric power the indution plates should heat.
