import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN)
GPIO.setup(26, GPIO.OUT)

while(True):
	if GPIO.input(21):
		GPIO.output(26,False)
	else:
		GPIO.output(26,True)
