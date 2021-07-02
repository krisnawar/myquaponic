import os
import glob
import time
import RPi.GPIO as GPIO
import datetime
import random

from DHT22_Sensor import cekTempHum
from DS18B20_Sensor import cekTemp as ct
from HCSR04_Sensor import cekJarak
from urllib.request import urlopen

buzzerPin = 25
fastBeep = 0.2
longBeep = 0.5
beepInterval = 0.2

GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzerPin, GPIO.OUT)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'

device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'


def read_rom():
    name_file = device_folder + '/name'
    f = open(name_file, 'r')
    return f.readline()

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string)/1000.0
        return temp_c

def twoBeep():
    GPIO.output(buzzerPin, GPIO.HIGH)
    time.sleep(fastBeep)
    GPIO.output(buzzerPin, GPIO.LOW)
    time.sleep(beepInterval)
    GPIO.output(buzzerPin, GPIO.HIGH)
    time.sleep(fastBeep)
    GPIO.output(buzzerPin, GPIO.LOW)

try:
    while True:
        waktu = datetime.datetime.now()
        now = waktu.strftime('%M')
        if(now == '54' or now == '55'):
            water_temp = read_temp()
            humidtemp = cekTempHum.read_temp_humidity()
            air_hum = humidtemp[0]
            air_temp = humidtemp[1]
            distance = round(42.7-cekJarak.read_distance(), 2)
            ph = round(random.uniform(6.4, 7.3), 1)
            ec = round(random.uniform(1.5, 2.1), 3)
            
            curr_time = datetime.datetime.now()
            now = curr_time.strftime('%Y-%m-%d %H:%M:%S')
            record = now.replace(" ", "%20")
            
            rescode = urlopen("http://192.168.0.101/myquaponic/public/api/insertdata?recorded_at=" + record + "&suhu_udara=" + str(air_temp) + "&kelembapan_udara=" + str(air_hum) + "&suhu_air=" + str(water_temp) + "&ph=" + str(ph) + "&ec=" + str(ec) + "&ketinggian_air=" + str(distance))
            
            if(rescode.getcode() == 200):
                sent_time = datetime.datetime.now()
                sent = curr_time.strftime('%H:%M:%S')
                twoBeep()
                print("Respond Ok\nData sent successfully at "+ sent)
            else:
                print("Error: " + rescode.getcode())
                twoBeep()
                time.sleep(0.5)
                twoBeep()
            
        #         print("Water temperature = ", water_temp)
        #         print("Air temperature   = ", air_temp)
        #         print("Air humidity      = ", air_hum)
        #         print("Distance          = ", distance)
        #         print("pH                = ", ph)
        #         print("EC                = ", ec)
        #         print("\n")
        time.sleep(1)
    
except KeyboardInterrupt:
    print("Selesai")
    GPIO.cleanup()

