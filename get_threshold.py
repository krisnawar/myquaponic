import time
import json
import sys
from urllib.request import urlopen

def writeThreshold():
    url = "https://myquaponic.xyz/api/getthreshold"
    response = urlopen(url)
    data_json = json.loads(response.read().decode())
#    print(data_json)
    t = open('idThreshold.txt')
    idt = t.readline().strip()
    t.close()
    if(idt != data_json[0]['id']):
        u = open('idThreshold.txt', 'w')
        u.writelines(data_json[0]['id'])
        u.close()

        f = open('threshold_data.txt', 'w')

        flist  = data_json[0]['w_pump_on'] + '\n'
        flist += data_json[0]['w_pump_off'] + '\n'
        flist += data_json[0]['a_pump_on'] + '\n'
        flist += data_json[0]['a_pump_off'] + '\n'
        flist += data_json[0]['low_ph'] + '\n'
        flist += data_json[0]['high_ph'] + '\n'
        flist += data_json[0]['low_rh'] + '\n'
        flist += data_json[0]['high_ec'] + '\n'
        flist += data_json[0]['w_height_low'] + '\n'
        flist += data_json[0]['w_height_high'] + '\n'
        flist += data_json[0]['feed_diff'] + '\n'
        f.writelines(flist)
        f.close()
#        print('fclose')

while True:
    try:
        writeThreshold()
        time.sleep(5)

    except KeyboardInterrupt:
        print('Selesai')
        sys.exit()

    except:
#        print('except')
        pass

