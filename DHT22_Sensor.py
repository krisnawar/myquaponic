import Adafruit_DHT
import time

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 17

class cekTempHum():
    def read_temp_humidity():
        time.sleep(2)
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        if humidity is not None and temperature is not None:
            temp = round(temperature, 1)
            humid = round(humidity, 1)
            returnValue = [humid, temp]
            return returnValue
        else:
            returnValue = [0,0]
            return returnValue
