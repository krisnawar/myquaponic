import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.output(20, 1)
GPIO.output(21, 1)

try:
	while True:
		GPIO.output(20, 0)
		time.sleep(2)
		GPIO.output(20, 1)
		time.sleep(5)

except KeyboardInterrupt:
	GPIO.cleanup()
