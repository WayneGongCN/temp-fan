import os
import logging
import json
from threading import Timer
from gpiozero import LED
from flask import Flask, Response


logging.basicConfig(level=logging.INFO, filename='temp_fan.log', filemode='a', format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
app = Flask(__name__)
fan = LED(4)


def get_temp ():
  tempFile = open('/sys/class/thermal/thermal_zone0/temp', 'r')
  temp = tempFile.readline()
  tempFile.close()
  temp = int(temp)/1000
  return temp


def get_fan_status ():
  return fan.value == 1


def set_fan (temp, fan_status):
  if temp > 55 and not(fan_status):
    logging.info("%s℃ FAN ON." % temp)
    fan.on()
  elif temp < 50 and fan_status:
    logging.info("%s℃ FAN OFF." % temp)
    fan.off()
  
  if temp > 60:
    logging.warning("TEMP: %s℃" % temp)
    os.system("curl https://sc.ftqq.com/{TOKEN}.send?text=树莓派温度警告:%s度" % temp)


def interval ():
  set_fan(get_temp(), get_fan_status())
  Timer(10, interval).start()


@app.route('/api/tempfan')
def tempfan():
  result = {
    'temp': get_temp(),
    'fanStatus': get_fan_status()
  }
  
  return Response(json.dumps(result), mimetype='application/json')


if __name__ == '__main__':
    interval()
    app.run(host='0.0.0.0')

