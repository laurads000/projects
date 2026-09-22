const int trig_pin = 12;
const int echo_pin = 11;

void setup() {
  pinMode(trig_pin, OUTPUT);
  pinMode(echo_pin, INPUT);

  digitalWrite(trig_pin, LOW);

  Serial.begin(9600);
}

void loop() {
  // Send a 10 μs trigger pulse
  digitalWrite(trig_pin, LOW);
  delayMicroseconds(2);

  digitalWrite(trig_pin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig_pin, LOW);

  // Measure how long ECHO stays HIGH
  unsigned long timing = pulseIn(echo_pin, HIGH);

  // Convert time to distance
  float distance = (timing * 0.0343) / 2;

  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  // Wait before taking another measurement
  delay(60);
}
