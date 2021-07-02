from urllib.request import urlopen

_air_temp = '30.0'
_air_humid = '80.0'
_water_temp = '29.0'
_ph = '7.0'
_ec = '0.2'
_water_height = '15'

class Temp_Data():
	def send_temp_data(at, ah, wt, ph, ec, wh):
		global _air_temp
		global _air_humid
		global _water_temp
		global _ph
		global _ec
		global _water_height

		try:
			_air_temp = str(at)
			_air_humid = str(ah)
			_water_temp = str(wt)
			_ph = str(ph)
			_ec = str(ec)
			_wh = str(wh)

#			print(_air_temp)
#			print(_air_humid)
#			print(_water_temp)
#			print(_ph)
#			print(_ec)
#			print(_wh)

			urlopen('https://myquaponic.xyz/api/update_temp_data?suhu_udara='+_air_temp+'&kelembapan_udara='+_air_humid+'&suhu_air='+_water_temp+'&ph='+_ph+'&ec='+_ec+'&ketinggian_air='+_wh)
#			print('success')

		except:
			print('error')
			pass

