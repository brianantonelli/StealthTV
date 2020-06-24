import logging
import yaml
import cec

from flask import Flask
from rpi_rf import RFDevice

logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)-15s - [%(levelname)s] %(module)s: %(message)s',)

with open('config.yml', 'r') as cf:
    cfg = yaml.load_all(cf, Loader=yaml.FullLoader)

app = Flask(__name__)

# fixme: move into class
rfdevice = RFDevice(cfg.lift.gpio)
rfdevice.enable_tx()
rfdevice.tx_repeat = cfg.lift.repeat

# fixme: move into class
cec.init()
cec_device = cec.Device(0)

def transmit_lift_code(code):
    logging.info('lift rf transmit: %s', code)
    rfdevice.tx_code(code, cfg.lift.protocol, cfg.lift.pulse, cfg.lift.length)

@app.route('/')
def index():
    return 'Hello World(s)'

@app.route('/move_lift/<direction>', methods=['POST'])
def move_lift(direction='up'):
    logging.info('move lift: %s', direction)
    if direction == 'up':
        transmit_lift_code(cfg.lift.code_up)
    else:
        transmit_lift_code(cfg.lift.code_down)

    return 'ok'

@app.route('/tv_power/<power>', methods=['POST'])
def tv_power(power='on'):
    logging.info('set tv power: %s', power)
    if power == 'on':
        cec_device.power_on()
        # TODO: switch input
    else:
        cec_device.standby()
        # TODO: does standby work with this lib or do we need to send the opcode?

    return 'ok'