import datetime
import time
import RPi.GPIO as GPIO
import serial
import threading
import os

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(22,GPIO.OUT,initial = GPIO.LOW)  # alarm siren
GPIO.setup(23,GPIO.OUT,initial = GPIO.LOW)  # fire siren
GPIO.setup(27,GPIO.OUT,initial = GPIO.LOW)  # alarm led on/off
GPIO.setup(17,GPIO.OUT,initial = GPIO.LOW)  # automatik light
GPIO.setup(12,GPIO.IN,pull_up_down = GPIO.PUD_UP)  # power detection
GPIO.setup(6,GPIO.IN,pull_up_down = GPIO.PUD_UP)  # rf control detection
GPIO.setup(5,GPIO.IN,pull_up_down = GPIO.PUD_UP)  # solar power detection
GPIO.setup(13,GPIO.IN,pull_up_down = GPIO.PUD_UP)  # tamper detection
GPIO.setup(20,GPIO.IN,pull_up_down = GPIO.PUD_UP)  # pir detection
GPIO.setup(21,GPIO.IN,pull_up_down = GPIO.PUD_UP)  # smoke detection

a='"'
b='"'
numbers=[12345678]  # list of phone numbers
status=""
status_counter=0
smswait=[]
camera_error_mesage=""
shd_time=["14:00"]
als=0  # auto light status

ser=serial.Serial("/dev/mod01",baudrate=9600,timeout = 5)  # gsm modem port
ser.close()

#########################  configure gsm modem for sending sms

ser.open()
ser.write("AT+CMGF=1\r")
time.sleep(3)
answer=ser.read(100)
ser.close()
print answer

#########################

def logwriter(mesage):

  mesagetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  log=mesagetime +" "+ mesage +"\n"
  print log
  f=open("rpialarm.log","a")
  f.write(log)
  f.close()

#########################

def siren():

  GPIO.output(22,GPIO.HIGH)
  GPIO.output(23,GPIO.HIGH)
  mesage="siren activated"
  logwriter(mesage) #>>
  time.sleep(40)
  GPIO.output(22,GPIO.LOW)
  GPIO.output(23,GPIO.LOW)
  mesage="siren deactivated"
  logwriter(mesage) #>>

#########################

def smswriter(mesage,numbers):

  global smswait

  if len(smswait)!=0:
    smswait.append(mesage)
    mesage=smswait
    mesage=str(mesage)
    mesage=mesage.replace(",","")
    mesage=mesage.replace("[","")
    mesage=mesage.replace("]","")
    mesage=mesage.replace("'","")
    print mesage
    for number in numbers:
      ser.open()
      ser.write("AT+CMGS="+a+str(number)+b+"\r")
      time.sleep(2)
      ser.write(mesage+chr(26))
      time.sleep(2)
      answer=ser.read(100)
      ser.close()
      mesage="mesage send to "+str(number)
      logwriter(mesage) #>>
      print answer
      smswait=[]

  elif len(smswait)==0:
    for number in numbers:
      ser.open()
      ser.write("AT+CMGS="+a+str(number)+b+"\r")
      time.sleep(2)
      ser.write(mesage+chr(26))
      time.sleep(2)
      answer=ser.read(100)
      ser.close()
      mesage="mesage send to "+str(number)
      logwriter(mesage) #>>
      print answer

  else:
    pass

#########################

def mobile_gsm(numbers):

  for number in numbers:
    ser.open()
    ser.write("ATD"+str(number)+";"+"\r")
    answer=ser.read(100)
    print answer
    time.sleep(20)
    ser.write("ATH"+"\r")
    answer=ser.read(100)
    ser.close()
    mesage="call send to "+str(number)
    logwriter(mesage) #>>
    print answer

#########################

def camera(foto_qt):

  global camera_error_mesage
  counter=0
  name="_photo.jpg"
  try:
    while foto_qt!=counter:
      time=datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
      photo_name=time+name
      os.system("wget -P /mnt/disk1/ http://192.168.5.7:8080/photo.jpg")
      os.chdir("/mnt/disk1/")
      os.rename("photo.jpg",photo_name)
      counter=counter+1
      os.chdir("/home/pi/")
  except:
    camera_error_mesage="camera error: foto not received"
    os.chdir("/home/pi/")
    logwriter(camera_error_mesage) #>>

#########################

def camera_error():

  global camera_error_mesage

  if camera_error_mesage!="":
    mesage=camera_error_mesage
    smswriter(mesage,numbers) #>>
    camera_error_mesage=""
  else:
    pass

#########################

camera(1)
camera_error()
mesage="rpialarm startup status: "
logwriter(mesage)
smswait.append(mesage)

#########################   # check status on startup

if GPIO.input(6)==1:
  mesage="alarm control off "
  status="off"
  logwriter(mesage) #>>
  smswait.append(mesage)
elif GPIO.input(6)==0:
  mesage="alarm control on "
  GPIO.output(27,GPIO.HIGH)
  status="on"
  logwriter(mesage) #>>
  smswait.append(mesage)
else:
  pass

#########################  # check power on startup

if GPIO.input(12)==1:
  mesage="error no power "
  logwriter(mesage) #>>
  smswait.append(mesage)
elif GPIO.input(12)==0:
  mesage="power status ok "
  logwriter(mesage) #>>
  smswait.append(mesage)
else:
  pass

#########################  # check automatik light on startup

if GPIO.input(5)==1:
  mesage="automatik light off "
  als=0
  logwriter(mesage) #>>
  smswait.append(mesage)
elif GPIO.input(5)==0:
  mesage="automatik light on "
  als=1
  logwriter(mesage) #>>
  smswait.append(mesage)
else:
  pass

#########################  # check tamper on startup

if GPIO.input(13)==1:
  mesage="tamper detected "
  logwriter(mesage) #>>
  smswait.append(mesage)
elif GPIO.input(13)==0:
  mesage="tamper status ok "
  logwriter(mesage) #>>
  smswait.append(mesage)
else:
  pass

#########################  # check pir on startup

if GPIO.input(20)==1:
  mesage="pir sensor activity detected "
  logwriter(mesage) #>>
  smswait.append(mesage)
elif GPIO.input(20)==0:
  mesage="pir sensor status ok "
  logwriter(mesage) #>>
  smswait.append(mesage)
else:
  pass

#########################  # check smoke sensor on startup

if GPIO.input(21)==1:
  mesage="smoke sensor status ok "
  logwriter(mesage) #>>
  smswait.append(mesage)
elif GPIO.input(21)==0:
  mesage="smoke sensor activated "
  logwriter(mesage) #>>
  smswait.append(mesage)
else:
  pass

#########################

mesage=""
smswriter(mesage,numbers)

#########################

def solar(self):

  global als

  if GPIO.input(5)==1:
    mesage="automatik light off"
    als=0
    GPIO.output(17,GPIO.LOW)
    print mesage
  elif GPIO.input(5)==0:
    mesage="automatik light on"
    als=1
    print mesage
  else:
    pass

GPIO.add_event_detect(5, GPIO.BOTH, callback = solar, bouncetime = 300)

#########################

def tamper(self):

  if GPIO.input(13)==1:
    mesage="tamper detected"
    foto_qt=5
    t1=threading.Thread(target=siren)
    t1.start() #>>
    t2=threading.Thread(target=camera,args=(foto_qt,))
    t2.start() #>>
    logwriter(mesage) #>>
    smswriter(mesage,numbers) #>>
    mobile_gsm(numbers) #>>
    camera_error() #>>
  elif GPIO.input(13)==0:
    mesage="tamper status ok"
    logwriter(mesage) #>>
    smswriter(mesage,numbers) #>>
  else:
    pass

GPIO.add_event_detect(13, GPIO.BOTH, callback = tamper, bouncetime = 300)

#########################

def pir(self):

  if status=="on":

    if GPIO.input(20)==1:
      mesage="pir sensor activity detected"
      foto_qt=5
      t1=threading.Thread(target=siren)
      t1.start() #>>
      t2=threading.Thread(target=camera,args=(foto_qt,))
      t2.start() #>>
      logwriter(mesage) #>>
      smswriter(mesage,numbers) #>>
      mobile_gsm(numbers) #>>
      camera_error() #>>
    elif GPIO.input(20)==0:
      mesage="pir sensor status ok"
      logwriter(mesage) #>>
      smswriter(mesage,numbers) #>>
    else:
      pass

  elif status=="off":

    if GPIO.input(20)==1:
      mesage="pir on"
      print mesage
      if als==1:
        GPIO.output(17,GPIO.HIGH)
        print "automatik light on"
      else:
        pass
    elif GPIO.input(20)==0:
      mesage="pir off"
      print mesage
      if als==1:
        GPIO.output(17,GPIO.LOW)
        print "automatik light off"
      else:
        pass
    else:
      pass

  else:
    pass

GPIO.add_event_detect(20, GPIO.BOTH, callback = pir, bouncetime = 300)

#########################

def smoke(self):

  if GPIO.input(21)==1:
    mesage="smoke sensor status ok"
    GPIO.output(23,GPIO.LOW)
    logwriter(mesage) #>>
    smswriter(mesage,numbers) #>>
  elif GPIO.input(21)==0:
    mesage="smoke sensor activated"
    GPIO.output(23,GPIO.HIGH)
    camera(5)
    logwriter(mesage) #>>
    smswriter(mesage,numbers) #>>
    mobile_gsm(numbers) #>>
    camera_error()
  else:
    pass

GPIO.add_event_detect(21, GPIO.BOTH, callback = smoke, bouncetime = 300)

#########################

def power(self):

  if GPIO.input(12)==1:
    mesage="power lost error"
    logwriter(mesage) #>>
    smswriter(mesage,numbers) #>>
  elif GPIO.input(12)==0:
    mesage="power restored"
    logwriter(mesage) #>>
    smswriter(mesage,numbers) #>>
  else:
    pass

GPIO.add_event_detect(12, GPIO.BOTH, callback = power, bouncetime = 300)

#########################

def rf(self):

  global status
  if GPIO.input(6)==1:
    mesage="alarm control off"
    GPIO.output(27,GPIO.LOW)
    status="off"
    camera(1)
    logwriter(mesage) #>>
    smswriter(mesage,numbers) #>>
    camera_error()
  elif GPIO.input(6)==0:
    mesage="alarm control on"
    GPIO.output(27,GPIO.HIGH)
    status="on"
    camera(1)
    logwriter(mesage) #>>
    smswriter(mesage,numbers) #>>
    camera_error()
  else:
    pass

GPIO.add_event_detect(6, GPIO.BOTH, callback = rf, bouncetime = 300)

#########################

while True:

  timenow = datetime.datetime.now().strftime('%H:%M')

  if status_counter==7200:  # send simple ok sms every 5 day > 432000 sec
    os.system("./clock.sh")
    mesage="alarm system status ok"
    print mesage
    smswriter(mesage,numbers) #>>
    status_counter=0
  else:
    status_counter=status_counter+1

  if timenow in shd_time:
    camera(1)
    camera_error()
  else:
    pass

  time.sleep(60)


# end



