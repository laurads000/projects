import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)

for i in range(25):
	GPIO.output(4, GPIO.HIGH)
	time.sleep(1)
	GPIO.output(4, GPIO.LOW)
	time.sleep(1)

GPIO.cleanup()
