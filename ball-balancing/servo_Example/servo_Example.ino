#include <Servo.h>

Servo servo;

void moveServo() {
    // 0 degrees
  servo.write(0);
  delay(1000);

  // 90 degrees
  servo.write(90);
  delay(1000);
  // 180 degrees
  servo.write(180);
  delay(1000);
}
void setup() {
  servo.attach(9);
  servo.write(0);

}

void loop() {

  // moveServo();
}
