from urllib.request import urlopen
import requests
import json

url = "https://myquaponic.xyz/api/getthreshold"
#response = requests.get(url)
response = urlopen(url)
datajson = json.loads(response.read().decode())
#print(response.text)
#print('abc')
#print(response.content)
print(datajson)
if (response.getcode() == 200):
    jsondata = response.json().decode()
    print('jsondata')
elif (response.getcode() == 404):
    print('404')
elif (response.getcode() == 502):
    print('502')
else:
    print(response.status_code)
