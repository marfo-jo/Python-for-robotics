// i2c_scanner: DIAGNOSTIC TOOL ONLY (like a multimeter for the I2C bus).
//
// It asks every 7-bit address "is anyone there?" and prints the ones that
// answer with an ACK. It does NOT talk to the MPU-6050's registers; that is
// your job in milestone 1.1. Use it to separate wiring faults from code faults:
// if the scanner can't see 0x68, no register code will work either.
//
// Upload: Arduino IDE > Tools > Board > Arduino Uno, Tools > Port > COMx,
// then Upload. Open Serial Monitor at 115200 baud.
#include <Wire.h>

const unsigned long SCAN_PERIOD_MS = 3000;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setWireTimeout(25000, true);  // never hang forever on a stuck bus
  Serial.println(F("# i2c_scanner: scanning 0x01..0x7E every 3 s"));
}

void loop() {
  uint8_t found = 0;
  for (uint8_t addr = 1; addr < 0x7F; addr++) {
    Wire.beginTransmission(addr);
    uint8_t err = Wire.endTransmission();
    if (err == 0) {
      Serial.print(F("found device at 0x"));
      if (addr < 0x10) Serial.print('0');
      Serial.println(addr, HEX);
      found++;
    } else if (err == 4 || err == 5) {
      Serial.print(F("bus error at 0x"));
      Serial.print(addr, HEX);
      Serial.println(err == 5 ? F(" (timeout: SDA or SCL stuck low?)") : F(" (other error)"));
    }
  }
  if (found == 0) {
    Serial.println(F("no devices found: check VCC, GND, SDA=A4, SCL=A5"));
  } else {
    Serial.print(F("scan done, devices: "));
    Serial.println(found);
  }
  Wire.clearWireTimeoutFlag();
  delay(SCAN_PERIOD_MS);
}
