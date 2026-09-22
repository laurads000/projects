#include <Servo.h>

Servo servo;

const int servoPin = 9;
const int trigPin = 12;
const int echoPin = 11;
const float targetDistance = 15.0;  // cm
const float tolerance = 0.5;        // cm
const int neutralAngle = 45;        // for servo
const int minAngle = 0;
const int maxAngle = 90;

int servoAngle = neutralAngle;

const int filterSize = 5;
float readings[filterSize] = {0};
int readIndex = 0;
float total = 0;

float Kp = 2.0;
float Ki = 0.0;
float Kd = 0.5;
float error = 0.0;
float prevError = 0.0;
float integral = 0.0;

unsigned long prevTime = 0;
const unsigned long updateTime = 50;  // PID update time, ms

float getDistance() {
  float dist = 0.0;
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  unsigned long timing = pulseIn(echoPin, HIGH, 30000UL); // 30ms timeout

  // Convert time to distance
  // 0.0343 --> sound of speed in cm/us
  dist = (timing * 0.0343) / 2;

  // outside valid distance OR sensor timeout
  if (dist > 400 || !timing) {
    return -1;
  }
  return dist;
}

float getFilteredDistance() {
  float newDist = getDistance();
  if (newDist == -1) return -1;

  total -= readings[readIndex];
  readings[readIndex] = newDist;
  total += newDist;
  readIndex = (readIndex + 1) % filterSize;

  return total / filterSize;
}

void setup() {
  servo.attach(servoPin);
  servo.write(servoAngle);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  digitalWrite(trigPin, LOW);

  Serial.begin(9600);

  // for distance filtering, prime with readings before controls start
  for (int i = 0; i < filterSize; i++) {
    float d = getDistance();
    if (d == -1) d = targetDistance; // fallback if a priming read fails
    readings[i] = d;
    total += d;
    delay(50);
  }

  prevTime = millis();
}


void loop() {
  // Only run PID every updateTime ms
  unsigned long currentTime = millis();

  if ((currentTime - prevTime) >= updateTime) {

    float distance = getFilteredDistance();

    // invalid distance from sensor 
    if (distance == -1) {
      prevTime = currentTime;
      return;
    }
    
    error = targetDistance - distance;
    float dt = (currentTime - prevTime) / 1000.0; // change in time in sec
    integral += error * dt;
    integral = constrain(integral, -50, 50);      // clamping
    float derivative = (error - prevError) / dt;  // accumulated error
    float output = (Kp*error)+ (Ki*integral) + (Kd*derivative);

    // updating servo angle
    servoAngle = neutralAngle + output;
    servoAngle = constrain(servoAngle, minAngle,maxAngle);
    servo.write(servoAngle);
    
    // updating values
    prevError = error;
    prevTime = currentTime;

    if (abs(error) <= tolerance) {
      Serial.println("Centered!");
    }
  }
}
