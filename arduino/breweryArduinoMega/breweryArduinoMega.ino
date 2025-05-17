#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 22 // Datenpin des DS18B20-Sensors

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// static adresses of the DS18B20 sensors
DeviceAddress sensorAddMash = { 0x28, 0xFF, 0xE3, 0x27, 0x6C, 0x18, 0x01, 0xF0 }; 
DeviceAddress sensorAddFill = { 0x28, 0xFF, 0x64, 0x02, 0xF7, 0x40, 0xB6, 0xC2 }; 
DeviceAddress sensorAddCook = { 0x28, 0xFF, 0x64, 0x02, 0xE9, 0x20, 0xEE, 0x3F }; 

// constant output pins for the heaters
const bool BOOL [2] = {LOW, HIGH};
const bool BOOLinv [2] = {HIGH, LOW}; // Für die Relaisplatine (muss invertiert angesteuert werden)
const int opSwitch [5] = { 24, 26, 28, 30, 32}; // Hand/Automatik Knebelschaltereingänge
const int relais [8] = { 23, 25, 27, 29, 31, 33, 35, 37};
const int alarmRelais = 3;
//const int mashPins [4] = { 34, 36, 38, 40};
//const int fillPins [4] = { 42, 44, 46, 48};
//const int cookPins [4] = { 49, 50, 51, 52};

const int heaters [3][4] = {
  { 34, 36, 38, 40},
  { 42, 44, 46, 48},
  { 49, 50, 51, 52}
};

unsigned long previousMillis = 0;
const long interval = 500; // in ms

int input = 0; // for incoming serial data


void setup() {
  
  Serial.begin(9600);
  Serial1.begin(9600);

  for (int i = 0; i < sizeof(opSwitch); i++) {
    pinMode(opSwitch[i], INPUT_PULLUP);
  }
  for (int i = 0; i < sizeof(relais); i++) {
    pinMode(relais[i],OUTPUT);
    digitalWrite(relais[i], HIGH);
  }
  for (int i = 0; i < sizeof(heaters); i++) {
    for (int j = 0; j < sizeof(heaters[i]); j++) {
      pinMode(heaters[i][j], OUTPUT);
      digitalWrite(heaters[i][j], LOW);
    }
  }
//  for (int i = 0; i < 4; i++) { //!!! Austauschen mit verschachtelter Schleife für 2-dimensionales Array
//    pinMode(opSwitch[i], INPUT_PULLUP);
//    pinMode(mashPins[i], OUTPUT);
//    pinMode(fillPins[i], OUTPUT);
//    pinMode(cookPins[i], OUTPUT);
//    digitalWrite(mashPins[i], LOW);
//    digitalWrite(fillPins[i], LOW);
//    digitalWrite(cookPins[i], LOW);
//  }
//  pinMode(opSwitch[4], INPUT_PULLUP);
  
  while (!Serial && !Serial1) {
    ;// waits for serial port to connect. Needed for native USB
  }
  
  sensors.begin();

  sensors.setResolution(sensorAddMash, 12);
  sensors.setResolution(sensorAddFill, 12);
  sensors.setResolution(sensorAddCook, 12);
  sensors.setWaitForConversion(true); // activate asynchrone temperature measurement (optional)

  Serial.println("setup ready");
}

void loop() {
  
  // ### WRITE #################################################################################################
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    sensors.requestTemperatures(); // requests temp values from all sensores

    float tempMash = sensors.getTempC(sensorAddMash); // temp value mash in Celsius
    float tempFill = sensors.getTempC(sensorAddFill); // temp value fill in Celsius
    float tempCook = sensors.getTempC(sensorAddCook);

    String switches = "";
    for (int i = 0; i < 5; i++) {
      switches = switches + digitalRead(opSwitch[i]);
    }
    //Serial1.println(switches);
    String data = String(tempMash) +";"+ String(tempFill) + ";" + String(tempCook) + ";" + switches + "\n"; // creates temp String to be sended
    //Serial.print("Sensordaten: " + data);
    const char* charData = data.c_str(); // creates a char-Array of the String (const char*)
    Serial1.write(charData, data.length()); // transfer the char-Array to the Raspberry Pi
  }

  digitalWrite(relais[0], BOOLinv[0]);
  digitalWrite(relais[2], BOOLinv[0]);
  digitalWrite(relais[4], BOOLinv[0]);
  digitalWrite(relais[5], BOOLinv[0]);
  digitalWrite(relais[6], BOOLinv[0]);
  digitalWrite(relais[7], BOOLinv[0]);
  
  // ### READ ##################################################################################################
  //Serial.println(Serial1.available());
  if (Serial1.available() >0) {
    String command = Serial1.readStringUntil(';');
    //Serial.println(command);
    input = command.toInt(); //!!! Jetzt könnte man die Parameter noch mit dem Raspberry vergleichen und sicherstellen, dass die beiden auf dem selben Stand sind
    Serial.println(String(input));

    digitalWrite(relais[alarmRelais], BOOLinv[input>>9]);

    for (int i = 2; i >= 0; i--){
      /*
       * Die Werte in value sind verdreht und gehen von 0 bis 7: (Da hängt mit der Ansteuerung der Bits für die Heizplatine zusammen)
       * 7 => Heizplatte aus
       * 1 => Heizplatte heizt mit minimaler Leistung
       * 0 => Heizplatte heizt mit maximaler Leistung
       */
      int value = ~(input >> (i*3)) & 7;
      Serial.print(command + " " + String(i*-1+3) + ": " + String(value*-1 +7) + " || ");
      if (i != 1) { // Weil der Nachguss mit der Steckdose gesteuert wird
        digitalWrite(heaters[i*-1+2][0], BOOL[value != 7]);
        value += 1;
        digitalWrite(heaters[i*-1+2][1], BOOL[(value>>2) & 1]);
        digitalWrite(heaters[i*-1+2][2], BOOL[(value>>1) & 1]);
        digitalWrite(heaters[i*-1+2][3], BOOL[ value     & 1]);
      } else {
        digitalWrite(relais[1], BOOLinv[value+1 <= 3]);
      }
    }
    Serial.println();
  } else { 
    digitalWrite(relais[1], BOOLinv[0]);
    digitalWrite(relais[3], BOOLinv[0]);
  }
}
