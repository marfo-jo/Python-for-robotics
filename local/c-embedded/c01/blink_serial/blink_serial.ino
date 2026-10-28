/*
 * C1 exercise 3: blink_serial (Arduino Uno, Arduino IDE on Windows)
 *
 * Copy this whole folder to my-solutions/c-embedded/c01/blink_serial/
 * (the folder name must match the .ino name), open the .ino in the
 * Arduino IDE, select board "Arduino Uno" and your COM port, then Upload.
 *
 * Goal: the on-board LED blinks once per second AND the Serial Monitor
 * (set to 115200 baud) shows:
 *   setup(): runs once
 *   loop(): blink 1
 *   loop(): blink 2
 *   ...
 */

unsigned long blinkCount = 0;  // survives between loop() calls (a global)

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);  // pin 13 on the Uno

  // TODO 1: start the serial port at 115200 baud with Serial.begin(...).

  // TODO 2: print the line "setup(): runs once" with Serial.println(...).
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
  delay(500);

  // TODO 3: add 1 to blinkCount.

  // TODO 4: print "loop(): blink " followed by blinkCount on ONE line.
  //         Hint: Serial.print(...) does not end the line; Serial.println(...) does.
}
