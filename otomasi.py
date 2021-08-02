# import necessary component
import os
import glob
import time
import RPi.GPIO as GPIO
import datetime
import random
import sys
import telepot

# import sensor library
from DHT22_Sensor import cekTempHum
#from HCSR04_Sensor import cekJarak
from PH_Sensor import PH
from TDS_Sensor import TDS

#import send realtime to server class
from temp_data import Temp_Data

#import component to send data to server
from urllib.request import urlopen

# set GPIO mode as BCM
GPIO.setmode(GPIO.BCM)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'

device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

#variable definition for DistanceSensor
TRIG = 23
ECHO = 24

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(18, GPIO.OUT)
servo1 = GPIO.PWM(18, 50)
servo1.start(0)

# variable definition for storing threshold data
t_wp_on = ""
t_wp_off = ""
t_ap_on = ""
t_ap_off = ""
t_lph = ""
t_hph = ""
t_lrh = ""
t_hec = ""
t_wh_l = ""
t_wh_h = ""
t_fd = ""

# initial boolean value for any anomaly present in the system
anom_ph = False
anom_rh = False
anom_ec = False
anom_wh = False

water_pump = False
air_pump = False

# sets output for relay as HIGH due to active low relay used
gpioList = [12, 16, 20, 21, 6, 13, 19, 26]

for i in gpioList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)

#user id definition to send telegram notification
tid = open('chat_id.txt')
id_balas = tid.readline().strip()
tid.close()
telegram_bot = telepot.Bot('1247524897:AAHAdZGhWNky6_gQfjAMduzVPhxqPDqiURM')

# define value for which gpio drive each relay module
wp_pond = 12
wp_plant = 16
ap_fil = 19
ap_pond = 26
acid = 20
base = 21
mist = 6
add_water = 13
feeding = 18

# sets initial value for water pump and air pump
z = open('threshold_data.txt','r')
p = datetime.datetime.strptime(z.readline().strip(), '%H:%M:%S')
t_wp_on_set = datetime.time(p.hour, p.minute, p.second)
q = datetime.datetime.strptime(z.readline().strip(), '%H:%M:%S')
t_wp_off_set = datetime.time(q.hour, q.minute, q.second)
r = datetime.datetime.strptime(z.readline().strip(), '%H:%M:%S')
t_ap_on_set = datetime.time(r.hour, r.minute, r.second)
s = datetime.datetime.strptime(z.readline().strip(), '%H:%M:%S')
t_ap_off_set = datetime.time(s.hour, s.minute, s.second)
z.close()
skrg = datetime.datetime.now()

# set initial value for first feeding
#t = datetime.datetime.strptime('22:13:00', '%H:%M:%S')
#f_feed = datetime.time(t.hour, t.minute, t.second)

if(skrg.time() < t_wp_on_set):
    water_pump = False
    
elif(skrg.time() > t_wp_on_set and skrg.time() < t_wp_off_set):
    water_pump = True
    
elif(skrg.time() > t_wp_off_set):
    water_pump = False
    
    
if(skrg.time() < t_ap_on_set):
    air_pump = False
    
elif(skrg.time() > t_ap_on_set and skrg.time() < t_ap_off_set):
    air_pump = True
    
elif(skrg.time() > t_ap_off_set):
    air_pump = False

#definition feeding related
mulai =  datetime.datetime.strptime('07:00', '%H:%M')
time_mulai = datetime.time(mulai.hour, mulai.minute)
future = datetime.datetime.now().replace(hour=7, minute=0)

flag_feed = True

midnight = datetime.datetime.strptime('23:59', '%H:%M')
time_midnight = datetime.time(midnight.hour, midnight.minute)

#definition boolean value for sending anomaly data
bool_sent = False	#telegram related
must_send = False	#server

q = open('api_key.txt')
API_KEY = q.readline().strip()
q.close()

#calculate distance
def read_distance(temp, humid):
    GPIO.output(TRIG, False)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    pulse_duration = pulse_duration/2

    speed = 331.4 + (0.606 * temp) + (0.0124 * humid)

    distance = pulse_duration * speed
    distance = distance * 100

    return distance
    
# calculate the water temp
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

#sending to server in case of anomaly
def send_anomaly(rec_at, a_temp, a_humid, w_temp, ph, ec, wh):
    bool_sent_anom = True
    curr_time = rec_at.strftime('%Y-%m-%d %H:%M:%S')
    record = curr_time.replace(" ", "%20")
    while(bool_sent_anom):
        try:
            print('sending anomali')
            urlopen('https://myquaponic.xyz/api/insertdata?api_key='+API_KEY+'&recorded_at='+record+'&suhu_udara='+str(a_temp)+'&kelembapan_udara='+str(a_humid)+'&suhu_air='+str(w_temp)+'&ph='+str(ph)+'&ec='+str(ec)+'&ketinggian_air='+str(wh))
            print('success sending anomali')
            bool_sent_anom = False

        except:
            print('telah terjadi kegagalan pengiriman ke server')
            pass

# begin loop
while True:
    try:
#       SET VALUE FOR EACH TRESHOLD
        f = open('threshold_data.txt','r')
        a = datetime.datetime.strptime(f.readline().strip(), '%H:%M:%S')
        t_wp_on = datetime.time(a.hour, a.minute, a.second)
        b = datetime.datetime.strptime(f.readline().strip(), '%H:%M:%S')
        t_wp_off = datetime.time(b.hour, b.minute, b.second)
        c = datetime.datetime.strptime(f.readline().strip(), '%H:%M:%S')
        t_ap_on = datetime.time(c.hour, c.minute, c.second)
        d = datetime.datetime.strptime(f.readline().strip(), '%H:%M:%S')
        t_ap_off = datetime.time(d.hour, d.minute, d.second)
        t_lph = float(f.readline().strip())
        t_hph = float(f.readline().strip())
        t_lrh = float(f.readline().strip())
        t_hec = float(f.readline().strip())
        t_wh_l = float(f.readline().strip())
        t_wh_h = float(f.readline().strip())
        t_fd = int(f.readline().strip())
        f.close()
#        t_fd = 2
        
#       RETRIEVE DATA FROM SENSOR
        humidtemp = cekTempHum.read_temp_humidity()
        while(humidtemp[0] == 0 or humidtemp[1] == 0):
            humidtemp = cekTempHum.read_temp_humidity()
        air_hum = humidtemp[0]
        air_temp = humidtemp[1]
        water_temp = read_temp()
        raw_distance = read_distance(air_temp, air_hum)
        while(raw_distance < 2.0 or raw_distance > 40.0):
            raw_distance =  read_distance(air_temp, air_hum)
        distance = round(40.4 - raw_distance, 2)
        ph = round(PH.getPHValue(water_temp), 2)
        tds = TDS.getTDSValue()/500
        ec = round(tds, 3)
        print('finish reading sensor')

        Temp_Data.send_temp_data(API_KEY, humidtemp[1], humidtemp[0], water_temp, ph, ec, distance)
#        print("Water temperature = ", water_temp)
#        print("Air temperature   = ", air_temp)
#        print("Air humidity      = ", air_hum)
#        print("Distance          = ", distance)
#        print("PH                = ", ph)
#        print("EC                = ", ec)
#        print("TDS               = ", TDS.getTDSValue())
#        GPIO.cleanup()
#        break
        
#        print("Halloo")
        
#       GET CURRENT TIME
        now = datetime.datetime.now()
        treset = now.strftime('%H:%M')        
        
#       AUTOMATION PROCESS
        message = ''
#       WATER PUMP CHECK
        if(now.time() < t_wp_on and water_pump == False):
#            print('Pompa air ikan menyala')
            GPIO.output(wp_pond, GPIO.LOW)
#            water_pump = True
            message += 'Pompa air kolam berhasil dihidupkan\n'
#            telegram_bot.sendMessage(id_balas, message)
            water_pump = True
        elif(now.time() > t_wp_on and now.time() < t_wp_off and water_pump == True):
#            print('Pompa air tumbuhan menyala\nPompa air ikan mati')
            GPIO.output(wp_pond, GPIO.HIGH)
            GPIO.output(wp_plant, GPIO.LOW)
#            water_pump = False
            message += 'Pompa air kolam berhasil dimatikan\nPompa tanaman berhasil dihidupkan\n'
#            telegram_bot.sendMessage(id_balas, message)
            water_pump = False
        elif(now.time() > t_wp_off and water_pump == False):
#            print('Pompa air ikan menyala')
            GPIO.output(wp_plant, GPIO.HIGH)
            GPIO.output(wp_pond, GPIO.LOW)
#            water_pump = True
            message += 'Pompa air berhasil dihidupkan\n'
#            telegram_bot.sendMessage(id_balas, message)
            water_pump = True
        elif(treset == '23:59' and water_pump == True):
#            print('Reset Bolean')
            water_pump = False
#        print('done water pump')

#       AIR PUMP CHECK
        if(now.time() < t_ap_on and air_pump == False):
#            print('Pompa udara filter menyala')
            GPIO.output(ap_fil, GPIO.LOW)
            message += 'Aerator filter berhasil dihidupkan\n'
#            telegram_bot.sendMessage(id_balas, message)
            air_pump = True
        elif(now.time() > t_ap_on and now.time() < t_ap_off and air_pump == True):
#            print('Pompa udara kolam menyala\nPompa udara filter mati')
            GPIO.output(ap_fil, GPIO.HIGH)
            GPIO.output(ap_pond, GPIO.LOW)
            message += 'Aerator kolam berhasil dihidupkan\nAerator filter berhasil dimatikan\n'
#            telegram_bot.sendMessage(id_balas, message)
            air_pump = False
        elif(now.time() > t_ap_off and air_pump == False):
#            print('Pompa udara filter menyala')
            GPIO.output(ap_pond, GPIO.HIGH)
            GPIO.output(ap_fil, GPIO.LOW)
            message += 'Aerator filter berhasil dihidupkan\n'
#            telegram_bot.sendMessage(id_balas, message)
            air_pump = True
        elif(treset == '23:59' and air_pump == True):
#            print('Reset Bolean')
            air_pump = False
#        print('done air pump')
        
#       PH VALUE CHECK
        if(now.time() > t_wp_on and now.time() < t_wp_off):
            if(ph < t_lph):
#                print('Pengisian buffer basa')
                if (bool_sent == False):
                    message += 'Air di kolam penampungan terlalu asam!!!\n'
                    message += 'pH saat ini : '+str(ph)+'\n'
                    message += 'Batas bawah pH : '+str(t_lph)+'\n'
                    message += 'Memulai prosedur penyesuain pH\n'
                    bool_sent = True
#                telegram_bot.sendMessage(id_balas, message)
                GPIO.output(base, GPIO.LOW)
                time.sleep(0.5)
                GPIO.output(base, GPIO.HIGH)
                must_send = True

            if(ph > t_lph and bool_sent == True):
                bool_sent = False
                
            if(ph > t_hph):
#                print('Pengisian buffer asam')
                if (bool_sent == False):
                    message += 'Air di kolam penampungan terlalu basa!!!\n'
                    message += 'pH saat ini : '+str(ph)+'\n'
                    message += 'Batas atas pH : '+str(t_hph)+'\n'
                    message += 'Memulai prosedur penyesuain pH\n'
                    bool_sent = True
#                telegram_bot.sendMessage(id_balas, message)
                GPIO.output(acid, GPIO.LOW)
                time.sleep(0.5)
                GPIO.output(acid, GPIO.HIGH)
                must_send = True

            if(ph < t_hph and bool_sent == True):
                bool_sent = False
#        print('done ph')
        
#       HUMIDITY CHECK
        if(air_hum < t_lrh):
#            print('Menyemprotkan misting')
            if (bool_sent == False):
                message += 'Kelembapan berada dibawah ambang batas!!!\n'
                message += 'Kelembapan saat ini : '+str(air_hum)+'\n'
                message += 'Batas bawah kelembapan : '+str(t_lrh)+'\n'
                message += 'Memulai prosedur penyemprotan kabut air\n'
                bool_sent = True
#            telegram_bot.sendMessage(id_balas, message)
            GPIO.output(mist, GPIO.LOW)
            time.sleep(2)
            GPIO.output(mist, GPIO.HIGH)
            must_send = True

        if(air_hum > t_lrh and bool_sent == True):
            bool_sent = False
#        print('done misting')
        
#       WATER LEVEL CHECK
        if(distance < t_wh_l and anom_wh == False):
#            print('menambahkan air kolam')
            if (bool_sent == False):
                message += 'Ketinggian air kolam kurang dari batas minimal!!!\n'
                message += 'Ketinggian air saat ini : '+str(distance)+'cm\n'
                message += 'Batas minimal : '+str(t_wh_l)+'cm\n'
                message += 'Memulai prosedur pengisian air\n'
                bool_sent = True
#            telegram_bot.sendMessage(id_balas, message)
            GPIO.output(add_water, GPIO.LOW)
            anom_wh = True
            must_send = True
#             
        if(distance > ((t_wh_l+t_wh_h)/2) and anom_wh == True):
#            print('stop menambahkan air kolam')
            GPIO.output(add_water, GPIO.HIGH)
            anom_wh = False
            message += 'Ketinggian air sudah normal\n'
            message += 'Ketinggian air saat ini : '+str(distance)+'\n'
#            telegram_bot.sendMessage(id_balas, message)
            anom_wh = False
            bool_sent = False
#        print('done water level')
        
#       EC CHECK
        if(ec > t_hec and distance < t_wh_h and anom_ec == False):
#            print('menambahkan air kolam karena ec tinggi')
            if (bool_sent == False):
                message += 'Air kolam terlalu pekat!\n'
                message += 'EC saat ini : '+str(ec)+'ms/cm\n'
                message += 'Batas maksimal EC : '+str(t_hec)+'ms/cm\n'
                message += 'Memulai prosedur pengisian air\n'
                bool_sent = True
#            telegram_bot.sendMessage(id_balas, message)
            GPIO.output(add_water, GPIO.LOW)
            anom_ec = True
            must_send = True

        if(ec < t_hec and anom_ec == True):
            GPIO.output(add_water, GPIO.HIGH)
            anom_ec = False
            bool_sent = False
            message += 'EC saat ini sudah normal dengan nilai : '+str(ec)+'ms/cm\n'
        
        if(distance > t_wh_h and anom_ec == True):
#            print('stop menambahkan air kolam karena ec tinggi')
            GPIO.output(add_water, GPIO.HIGH)
            anom_ec = False
            bool_sent = False
            message += 'Ketinggian air kolam sudah melebihi batas\nSilahkan cek kolam untuk memastikan kadar EC\n'
            message += '\nJika kadar EC lebih dari '+str(t_hec)+'ms/cm, dimohon untuk menguras kolam'
#            telegram_bot.sendMessage(id_balas, message)
#        print('done ec')
            
#       AUTO FEEDING
#       FIRST FEEDING
#        print('sebelum feeding')
#        print(now.strftime('%H:%M'))
#        print('future : '+future.strftime('%H:%M'))
        if (now.strftime('%H:%M') >= time_mulai.strftime('%H:%M') and now.strftime('%H:%M') <= time_midnight.strftime('%H:%M')):
            if (now.strftime('%H:%M') == time_mulai.strftime('%H:%M') and flag_feed):
#                print('MEMBERI MAKAN')
                servo1.ChangeDutyCycle(7)
                time.sleep(0.3)
                servo1.ChangeDutyCycle(2)
                time.sleep(0.5)
                servo1.ChangeDutyCycle(0)
                jam_tambah = datetime.timedelta(hours = t_fd)
                future = now + jam_tambah
                flag_feed = False
                message += 'Pemberian pakan pukul : '+now.strftime('%H:%M')+'\n'
#            print(future.strftime('%H:%M'))
            if (now.strftime('%H:%M') == future.strftime('%H:%M') and flag_feed):
#                print('MEMBERI MAKAN LAGI')
                servo1.ChangeDutyCycle(7)
                time.sleep(0.3)
                servo1.ChangeDutyCycle(2)
                time.sleep(0.5)
                servo1.ChangeDutyCycle(0)
                jam_tambah = datetime.timedelta(hours = t_fd)
                future = now + jam_tambah
                flag_feed = False
                message += 'Pemberian pakan pukul : '+now.strftime('%H:%M')+'\n'
            while(future < now):
                jam_tambah = datetime.timedelta(hours = t_fd)
                future = future + jam_tambah
#                print((future))
#                time.sleep(1)

            if (now.strftime('%H:%M') != future.strftime('%H:%M') and now.strftime('%H:%M') != time_mulai.strftime('%H:%M')):
#                print('If terakhir')
                flag_feed = True
#        print('done feeding')

#        try:
        if (message != '' and must_send == True):
            send_anomaly(now, air_temp, air_hum, water_temp, ph, ec, distance)
        if(message != ''):
#            print('try tele')
#            print(message)
            tele = True
            while(tele):
                try:
                    telegram_bot.sendMessage(id_balas, message)
#            print('after tele')
                    tele = False

                except:
                    print('gagal tele')

#            print('success tele')
#            else:
#                print('Message kosong')
#        except:
#            print('gagal tele')
#            print('Gagal mengirim : '+message)
#            time.sleep(40)
#            pass

        time.sleep(1)

    except KeyboardInterrupt:
        print("Selesai")
        servo1.stop()
        GPIO.cleanup()
        sys.exit()

    except:
        print('terjadi exception')
        pass
