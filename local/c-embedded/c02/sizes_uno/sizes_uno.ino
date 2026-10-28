/*
 * C2 exercise 3: sizes_uno (Uno half of the VM-vs-Uno comparison)
 *
 * Copy this folder to my-solutions/c-embedded/c02/sizes_uno/, open it in
 * the Arduino IDE (board "Arduino Uno"), upload, and open the Serial
 * Monitor at 115200 baud. Print the SAME 12 lines, in the SAME format, as
 * your desktop sizes.c, then compare the two outputs line by line.
 *
 * The Uno's printf() is not wired to Serial, so use Serial.print/println.
 */
#include <stdint.h>
#include <limits.h>

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    // On the Uno this returns at once; on USB-native boards it waits.
  }

  Serial.print("sizeof(char) = ");
  Serial.println(sizeof(char));

  // TODO 1: short, int, long, long long, float, double (same format).

  // TODO 2: uint8_t, int16_t, uint32_t.

  // TODO 3: "INT_MAX = ..." and "LONG_MAX = ...".

  // TODO 4 (the classic bug): store millis()-sized numbers in an int.
  //   int fromMillis = (int)40000UL;
  //   Serial.print("(int)40000 = ");
  //   Serial.println(fromMillis);
  // Predict the value BEFORE you upload. Explain it in a comment.
}

void loop() {
  // Nothing to repeat: everything runs once in setup().
}
