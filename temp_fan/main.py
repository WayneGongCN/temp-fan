import os
import logging
import json
from threading import Timer
from gpiozero import LED
from flask import Flask, Response

FAN_GPIO = 4
SERVER_CHAN_TOKEN = ''

temp_max = 55
temp_min = 50
temp_warning = 60

logging.basicConfig(level=logging.INFO, filename='temp_fan.log', filemode='a', format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
app = Flask(__name__)
fan = LED(FAN_GPIO)


def get_temp ():
  tempFile = open('/sys/class/thermal/thermal_zone0/temp', 'r')
  temp = tempFile.readline()
  tempFile.close()
  temp = int(temp)/1000
  return temp


def get_fan_status ():
  return fan.value == 1


def set_fan (temp, fan_status):
  if temp > temp_max and not(fan_status):
    logging.info("%s℃ FAN ON." % temp)
    fan.on()
  elif temp < temp_min and fan_status:
    logging.info("%s℃ FAN OFF." % temp)
    fan.off()
  
  if temp > temp_warning:
    logging.warning("TEMP: %s℃" % temp)
    os.system("curl https://sc.ftqq.com/%s.send?text=树莓派温度警告:%s度" % (SERVER_CHAN_TOKEN, temp))


def interval ():
  set_fan(get_temp(), get_fan_status())
  Timer(10, interval).start()


@app.route('/api/tempfan')
def tempfan():
  result = {
    'config': {
    'tempWarning': temp_warning,
    'tempMax': temp_max,
    'tempMin': temp_min,
    },
    'temp': get_temp(),
    'fanStatus': get_fan_status()
  }
  
  return Response(json.dumps(result), mimetype='application/json')


if __name__ == '__main__':
    interval()
    app.run(host='0.0.0.0')

