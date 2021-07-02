import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

TRIG = 23
ECHO = 24

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

class cekJarak():
    def read_distance(temp, humid):
        GPIO.output(TRIG, False)
        
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        
        while GPIO.input(ECHO)==0:
            pulse_start = time.time()
            
        while GPIO.input(ECHO)==1:
            pulse_end = time.time()
        
        pulse_duration = pulse_end - pulse_start
        pulse_duration = pulse_duration/2

        speed = 331.4 + (0.606*temp) + (0.0124*humid)

        distance = speed * pulse_duration
        distance = distance * 100
        
#        distance = pulse_duration * 17449
        
#        distance = round(distance, 2)
        
        return distance
