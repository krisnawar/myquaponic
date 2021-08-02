from urllib.request import urlopen
import time
import datetime

_api_key = 'c4ca4238a0b923820dcc509a6f75849b'
_air_temp = '30.0'
_air_humid = '80.0'
_water_temp = '29.0'
_ph = '7.0'
_ec = '0.2'
_water_height = '15'

class Temp_Data():
	def send_temp_data(api_key, at, ah, wt, ph, ec, wh):
#		print('function terpanggil')
		global _air_temp
		global _air_humid
		global _water_temp
		global _ph
		global _ec
		global _water_height
#		print('declare time')
		first = datetime.datetime.strptime('00:10', '%M:%S')
		first_timestamp = datetime.time(first.hour, first.minute, first.second)
		second = datetime.datetime.strptime('30:00', '%M:%S')
		second_timestamp = datetime.time(second.hour, second.minute, second.second)
		third = datetime.datetime.strptime('30:10', '%M:%S')
		third_timestamp = datetime.time(third.hour, third.minute, third.second)
		now = datetime.datetime.now()
#		print(now.strftime('%H:%M:%S'))
#		try:
		if(now.strftime('%M:%S') < first_timestamp.strftime('%M:%S') or (now.strftime('%M:%S') > second_timestamp.strftime('%M:%S') and now.strftime('%M:%S') < third_timestamp.strftime('%M:%S'))):
#			print('if')
			now = datetime.datetime.now()
			time.sleep(1)
#		print('exit while')
		else:
			_api_key = str(api_key)
			_air_temp = str(at)
			_air_humid = str(ah)
			_water_temp = str(wt)
			_ph = str(ph)
			_ec = str(ec)
			_wh = str(wh)

			urlopen('https://myquaponic.xyz/api/update_temp_data?api_key='+_api_key+'&suhu_udara='+_air_temp+'&kelembapan_udara='+_air_humid+'&suhu_air='+_water_temp+'&ph='+_ph+'&ec='+_ec+'&ketinggian_air='+_wh)
#			print('success')

#		except:
#			print('error')
#			pass

#		except KeyboardInterrupt:
#			print('Selesai')
