#include <OneWire.h>
#include <DallasTemperature.h>


#define ONE_WIRE_BUS 22 // Datenpin des DS18B20-Sensors

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// static adresses of the DS18B20 sensors
// Alte Adressen:
// { 0x28, 0xFF, 0x64, 0x02, 0xF7, 0x57, 0x99, 0x22 }
// { 0x28, 0xFF, 0x64, 0x02, 0xF7, 0x57, 0x99, 0x22 }
DeviceAddress sensorAddMash = { 0x28, 0xFF, 0x01, 0x18, 0x6C, 0x27, 0xE3, 0xFF }; 
DeviceAddress sensorAddFill = { 0x28, 0xFF, 0xB6, 0x40, 0xF7, 0x02, 0x64, 0xFF }; 
DeviceAddress sensorAddCock = { 0x28, 0xFF, 0xEE, 0x20, 0xE9, 0x02, 0x64, 0xFF }; 

const bool BOOL [2] = {LOW, HIGH};
const int opSwitch [5] = { 24, 26, 28, 30, 32};
const int notAusPin = 53;
const int alarmRelais = 3; // wird noch geändert
const int relaisPlat [8] = { 23, 25, 27, 29, 31, 33, 35, 37}; // werden mit 0V geschalten
const int mashPins [4] = { 34, 36, 38, 40};
const int fillPins [4] = { 42, 44, 46, 48};
const int cookPins [4] = { 49, 50, 51, 52};

unsigned long previousMillis = 0;
const long interval = 500; // in ms

void setup() {
  
  Serial.begin(9600);
  
  pinMode(alarmPin,OUTPUT);
  digitalWrite(alarmPin, LOW);
  for (int i = 0; i < 4; i++) {
    pinMode(opSwitch[i], INPUT_PULLUP);
    pinMode(mashPins[i], OUTPUT);
    pinMode(fillPins[i], OUTPUT);
    pinMode(cookPins[i], OUTPUT);
    digitalWrite(mashPins[i], LOW);
    digitalWrite(fillPins[i], LOW);
    digitalWrite(cookPins[i], LOW);
  }
  pinMode(opSwitch[4], INPUT_PULLUP);
  
  while (!Serial) {
    ;// waits for serial port to connect. Needed for native USB
  }
  
  sensors.begin();

  sensors.setResolution(sensorAddress1, 12);
  sensors.setResolution(sensorAddress2, 12);
  sensors.setWaitForConversion(true); // activate asynchrone temperature measurement (optional)

}

void loop() {
  
  // ### WRITE #################################################################################################
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    sensors.requestTemperatures(); // requests temp values from all sensores

    float temp1 = sensors.getTempC(sensorAddress1); // temp value mash in Celsius
    float temp2 = sensors.getTempC(sensorAddress2); // temp value fill in Celsius

    // Serial.println(temp1);
    // !!! 69 muss noch mit der Temperatur des 3. Sensor ausgetauscht werden

    String switches = "";
    for (int i = 0; i < 5; i++) {
      switches = switches + digitalRead(opSwitch[i]);
    }
    Serial1.println(switches);
    String data = String(temp1) +";"+ String(temp2) + ";69;" + switches + "\n"; // creates temp String to be sended
    const char* charData = data.c_str(); // creates a char-Array of the String (const char*)
    Serial.write(charData, data.length()); // transfer the char-Array to the Raspberry Pi
    //Serial.write("10;20;30;11111\n".c_str(), "10;20;30;11111\n".length());
  }
  // ### READ ##################################################################################################
  if (Serial.available() >0) {
    String command = Serial.readStringUntil(';');
    if (command.charAt(0) == 'a') {
      digitalWrite(alarmPin, BOOL[command.charAt(1) - '0']);
    }
    if (command.charAt(0) == 'm') {
      controllHeater (mashPins, command.charAt(1), command.charAt(2) - '0');
    }
    if (command.charAt(0) == 'f') {
      controllHeater (fillPins, command.charAt(1), command.charAt(2) - '0');
    }
    if (command.charAt(0) == 'c') {
      controllHeater (cookPins, command.charAt(1), command.charAt(2) - '0');
    }
    // !!! Die Ansteuerungen der weitern Heizplatten müssen noch eingefügt werden
  }
}

void controllHeater (int heater[], char action, int value) {
  if (action == 'o') {
    digitalWrite(heater[0], BOOL[value]);
  } else if (action == 'v') {
    switch (value) {
      case 8:
        writeValue(heater, 0, 0, 0);
        break;
      case 7:
        writeValue(heater, 0, 0, 1);
        break;
      case 6:
        writeValue(heater, 0, 1, 0);
        break;
      case 5:
        writeValue(heater, 0, 1, 1);
        break;
      case 4:
        writeValue(heater, 1, 0, 0);
        break;
      case 3:
        writeValue(heater, 1, 0, 1);
        break;
      case 2:
        writeValue(heater, 1, 1, 0);
        break;
      case 1:
        writeValue(heater, 1, 1, 1);
        break;
    }
  } /*else if (action == 'c') {
    // could eventually be removed, because the programm do not tell when take the controll for the induction heater
    digitalWrite(heater[4], BOOL[value]);
  }*/
}

void writeValue (int heater[], int bit2, int bit1, int bit0) {
  digitalWrite(heater[1], BOOL[bit2]);
  digitalWrite(heater[2], BOOL[bit1]);
  digitalWrite(heater[3], BOOL[bit0]);
}
