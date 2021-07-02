import os
import glob
import time
import RPi.GPIO as GPIO
import datetime
import random
import sys
import json

from DHT22_Sensor import cekTempHum
from HCSR04_Sensor import cekJarak
from PH_Sensor import PH
from TDS_Sensor import TDS
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
code_dir = '/home/pi/Desktop/Coding/skripsi/'

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
    
#def writeThreshold():
#    url = "https://myquaponic.xyz/api/getthreshold"        
#    response = urlopen(url)        
#    data_json = json.loads(response.read().decode())
#    t=open('idThreshold.txt')
#    idt=t.readline().strip()
#    t.close()
#    if(idt != data_json[0]['id']):
#        u = open('idThreshold.txt', 'w')
#        u.writelines(data_json[0]['id'])
#        u.close()
    
#        f=open('threshold_data.txt','w')
    
#        flist   = data_json[0]['w_pump_on'] + '\n'
#        flist  += data_json[0]['w_pump_off'] + '\n'
#        flist  += data_json[0]['a_pump_on'] + '\n'
#        flist  += data_json[0]['a_pump_off'] + '\n'
#        flist  += data_json[0]['low_ph'] + '\n'
#        flist  += data_json[0]['high_ph'] + '\n'
#        flist  += data_json[0]['low_rh'] + '\n'
#        flist  += data_json[0]['high_ec'] + '\n'
#        flist  += data_json[0]['w_height_low'] + '\n'
#        flist  += data_json[0]['w_height_high'] + '\n'
#        flist  += data_json[0]['feed_diff'] + '\n'
#        f.writelines(flist)
#        f.close()

def twoBeep():
    GPIO.output(buzzerPin, GPIO.HIGH)
    time.sleep(fastBeep)
    GPIO.output(buzzerPin, GPIO.LOW)
    time.sleep(beepInterval)
    GPIO.output(buzzerPin, GPIO.HIGH)
    time.sleep(fastBeep)
    GPIO.output(buzzerPin, GPIO.LOW)
    time.sleep(beepInterval)
    
def threeBeep():
    GPIO.output(buzzerPin, GPIO.HIGH)
    time.sleep(fastBeep)
    GPIO.output(buzzerPin, GPIO.LOW)
    time.sleep(beepInterval)
    GPIO.output(buzzerPin, GPIO.HIGH)
    time.sleep(fastBeep)
    GPIO.output(buzzerPin, GPIO.LOW)
    time.sleep(beepInterval)
    GPIO.output(buzzerPin, GPIO.HIGH)
    time.sleep(fastBeep)
    GPIO.output(buzzerPin, GPIO.LOW)
    time.sleep(beepInterval)

if __name__ == '__main__':
    try:
#        print('masuk try')
#        waktu = datetime.datetime.now()
#        now = waktu.strftime('%M:%S')
#        detik = int(waktu.strftime('%S'))
#        print(detik)
#        if(now == '00:00' or now == '30:00'):
        water_temp = read_temp()
        humidtemp = cekTempHum.read_temp_humidity()
        while (humidtemp[0] == 0 or humidtemp[1] == 1):
            humidtemp = cekTempHum.read_temp_humidity()
        air_hum = humidtemp[0]
        air_temp = humidtemp[1]
        raw_distance = cekJarak.read_distance(air_temp, air_hum)
        while (raw_distance < 2.0 or raw_distance > 40.0):
            raw_distance = cekJarak.read_distance(air_temp, air_hum)
        distance = round(41.2 - raw_distance, 2)
        ph = round(PH.getPHValue(water_temp), 2)
        tds = TDS.getTDSValue()/500
        ec = round(tds, 3)
#        print('selesai baca sensor')
            
        curr_time = datetime.datetime.now()
        now = curr_time.strftime('%Y-%m-%d %H:%M:%S')
        record = now.replace(" ", "%20")
            
#             print("Water temperature = ", water_temp)
#             print("Air temperature   = ", air_temp)
#             print("Air humidity      = ", air_hum)
#             print("Distance          = ", distance)
#             print("pH                = ", ph)
#             print("EC                = ", ec)
#        print('bersiap urlopen')
        rescode = urlopen("https://myquaponic.xyz/api/insertdata?recorded_at=" + record + "&suhu_udara=" + str(air_temp) + "&kelembapan_udara=" + str(air_hum) + "&suhu_air=" + str(water_temp) + "&ph=" + str(ph) + "&ec=" + str(ec) + "&ketinggian_air=" + str(distance))
            
        if(rescode.getcode() == 200):
#                sent_time = datetime.datetime.now()
#                sent = curr_time.strftime('%H:%M:%S')
            twoBeep()
            GPIO.cleanup()
        
        else:
            threeBeep()
            GPIO.cleanup()
        
#        if(detik%5 == 0):
#            writeThreshold()
            
#        time.sleep(1)
    
    except KeyboardInterrupt:
        print("Selesai")
        GPIO.cleanup()

#except:
#    print('Program berhenti karena terjadi error')
#    GPIO.cleanup()
