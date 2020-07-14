import logging
import yaml
import cec
import RPi.GPIO as GPIO
import atexit

from flask import Flask
from rpi_rf import RFDevice

logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)-15s - [%(levelname)s] %(module)s: %(message)s',)

with open('config.yml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

app = Flask(__name__)

# fixme: move into class
rfdevice = RFDevice(cfg['lift']['gpio'])
rfdevice.enable_tx()
rfdevice.tx_repeat = cfg['lift']['repeat']

# fixme: move into class
# cec.init()
# cec_device = cec.Device(0)

def transmit_lift_code(code):
    logging.info('lift rf transmit: %s; protocol: %s; pulse length: %d, length: %d', code, cfg['lift']['protocol'], cfg['lift']['pulse'], cfg['lift']['length'])
    rfdevice.tx_code(code, cfg['lift']['protocol'], cfg['lift']['pulse'], cfg['lift']['length'])

def at_shutdown():
    logging.info('Shutting down, cleaning up RFDevice and GPIO..')
    rfdevice.cleanup()
    GPIO.cleanup()


atexit.register(at_shutdown)

@app.route('/')
def index():
    return 'Hello World(s)'

@app.route('/move_lift/<direction>', methods=['POST'])
def move_lift(direction='up'):
    logging.info('move lift: %s', direction)
    if direction == 'up':
        transmit_lift_code(cfg['lift']['code']['up'])
    else:
        transmit_lift_code(cfg['lift']['code']['down'])

    return 'ok'

@app.route('/tv_power/<power>', methods=['POST'])
def tv_power(power='on'):
    logging.info('set tv power: %s', power)
    destination = cec.CECDEVICE_BROADCAST

    if power == 'on':
        cec_device.power_on()
    else:
        cec_device.standby()
        # opcode = cec.CEC_OPCODE_STANDBY
        # cec.transmit(destination, opcode, str.encode(cfg.tv.code.on))

    return 'ok'


# if __name__ == "__main__":
#     logging.info("StealthTV listening on 0.0.0.0:{}".format(cfg['app']['port']))
#     app.run(host="127.0.0.1:{}".format(cfg['app']['port']), debug=True)
