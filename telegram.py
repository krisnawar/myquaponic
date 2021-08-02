import os
import glob
import time
import datetime
import telepot
import RPi.GPIO as GPIO
from telepot.loop import MessageLoop
from DHT22_Sensor import cekTempHum
from HCSR04_Sensor import cekJarak
from PH_Sensor import PH
from TDS_Sensor import TDS

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'

device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

buzzer = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer, GPIO.OUT)

def beep():
	GPIO.output(buzzer, GPIO.HIGH)
	time.sleep(0.1)
	GPIO.output(buzzer, GPIO.LOW)
	time.sleep(0.1)


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

def action(msg):
	chat_id = msg['chat']['id']
	command = str(msg['text']).lower()

	if '/cek_suhu_kelembapan' in command:
		beep()
		humidity = cekTempHum.read_temp_humidity()
		humid = str(humidity[0])
		temp = str(humidity[1])
		message = 'Suhu udara saat ini : '+temp+'°C\nKelembapan udara saat ini : '+humid+'%'
		telegram_bot.sendMessage(chat_id, message)
		beep()
		beep()

	elif '/cek_suhu_air' in command:
		beep()
		temp = str(read_temp())
		message = 'Suhu air saat ini : '+temp+'°C'
		telegram_bot.sendMessage(chat_id, message)
		beep()
		beep()

	elif '/cek_ketinggian_air' in command:
		beep()
		humidity = cekTempHum.read_temp_humidity()
		humid = humidity[0]
		temp = humidity[1]
		distance = str(round(41.2 - cekJarak.read_distance(temp, humid), 2))
		message = 'Ketinggian air saat ini : '+distance+'cm'
		telegram_bot.sendMessage(chat_id, message)
		beep()
		beep()

	elif '/cek_ph' in command:
		beep()
		temp = read_temp()
		ph = str(round(PH.getPHValue(temp), 2))
		message = 'PH saat ini : '+ph
		telegram_bot.sendMessage(chat_id, message)
		beep()
		beep()

	elif 'cek_tds_ec' in command:
		beep()
		tds = TDS.getTDSValue()
		ec = str(round(tds/500, 3))
		message = 'TDS saat ini : '+str(round(tds, 2))+' ppm\nEC saat ini : '+ec+' ms/cm'
		telegram_bot.sendMessage(chat_id, message)
		beep()
		beep()

	elif '/show_threshold' in command:
		beep()
		f = open('threshold_data.txt','r')
		t_wp_on = f.readline().strip()
		t_wp_off = f.readline().strip()
		t_ap_on = f.readline().strip()
		t_ap_off = f.readline().strip()
		t_lph = f.readline().strip()
		t_hph = f.readline().strip()
		t_lrh = f.readline().strip()
		t_hec = f.readline().strip()
		t_wh_l = f.readline().strip()
		t_wh_h = f.readline().strip()
		t_fd = f.readline().strip()
		f.close

		message  = 'Berikut ini settingan threshold/batas:\n'
		message += '\nPompa tanaman hidup jam '+t_wp_on
		message += '\nPompa tanaman mati jam '+t_wp_off
		message += '\nAerator kolam hidup jam '+t_ap_on
		message += '\nAerator kolam mati jam '+t_ap_off
		message += '\nBatas pH terendah = '+t_lph
		message += '\nBatas pH tertinggi = '+t_hph
		message += '\nBatas kelembapan terendah = '+t_lrh+'%'
		message += '\nBatas EC tertinggi = '+t_hec+' ms/cm'
		message += '\nBatas air terendah = '+t_wh_l+' cm'
		message += '\nBatas air tertinggi = '+t_wh_h+' cm'
		message += '\nPemberian pakan = '+t_fd+' jam sekali.'
		telegram_bot.sendMessage(chat_id, message)
		beep()
		beep()

	elif '/get_chat_id' in command:
		beep()
		message = 'Chat ID anda adalah = '+ str(chat_id)
		telegram_bot.sendMessage(chat_id, message)
		beep()
		beep()

	elif '/help' in command:
		beep()
		message  = 'SELAMAT DATANG\n'
		message += '\nKenalin nih, aku Bot MyQuaponic.\nKamu bisa pantau sistem akuaponikmu lewat bot ini lho\n'
		message += '\nSilahkan pake command berikut yaa..\n'
		message += '\n/cek_suhu_kelembapan - cek suhu & kelembapan'
		message += '\n/cek_suhu_air - cek suhu air'
		message += '\n/cek_ketinggian_air - cek ketinggian air'
		message += '\n/cek_ph - cek pH'
		message += '\n/cek_tds_ec - cek TDS & EC\n'
		message += '\n/show_threshold - kalo mau liat batas thresholdnya\n'
		message += '\nSegitu dulu yaa 😊'
		message += '\nSelamat berakuaponik 😉'
		telegram_bot.sendMessage(chat_id, message)
		beep()
		beep()

	else:
		beep()
		message  = 'Maaf, command nggak dikenali nih.'
		message += '\nSilahkan klik command /help buat ngeliat command yang tersedia.\n'
		message += 'Makasih 😉'
		telegram_bot.sendMessage(chat_id, message)
		beep()
		beep()

telegram_bot = telepot.Bot('1247524897:AAHAdZGhWNky6_gQfjAMduzVPhxqPDqiURM')

MessageLoop(telegram_bot, action).run_as_thread()

try:
	while 1:
		time.sleep(10)

except KeyboardInterrupt:
	GPIO.cleanup()

