import time
import RPi.GPIO as GPIO
import os

GPIO.setmode(GPIO.BCM)

pbtn = 26
rbtn = 19

GPIO.setup(pbtn,GPIO.IN)
GPIO.setup(rbtn,GPIO.IN)

def power(pbtn):
  os.system("wall 'Power button pressed' ")
  time.sleep(3)
  os.system("sudo poweroff")  

def restart(rbtn):
  os.system("wall 'Reset button pressed' ")
  time.sleep(3)
  os.system("sudo reboot")

GPIO.add_event_detect(pbtn,GPIO.FALLING,callback = power,bouncetime = 300)
GPIO.add_event_detect(rbtn,GPIO.FALLING,callback = restart,bouncetime = 300)

while True:

  time.sleep(100)
