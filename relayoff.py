#!/usr/bin/python
# Group 36 (Ng Chee Ming and Lee Jia En)
# Trigger from an AWS rule with the actuating of buzzer.

import RPi.GPIO as GPIO  
from time import time  
  
#GPIO.setmode(GPIO.BOARD)  
#GPIO.setwarnings(False)
#number = 40
#GPIO.setup(number,GPIO.OUT)  
#GPIO.output(number,True)


GPIO.setmode(GPIO.BCM)  
number = 21  
GPIO.setup(number, GPIO.OUT)  
GPIO.output(number, GPIO.LOW) 
