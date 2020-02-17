import argparse
import logging
import math

import piglow

from pythonosc import dispatcher
from pythonosc import osc_server

from PCA9685 import PCA9685

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('IMU')
logger.setLevel(logging.INFO)

last_change = 0

def mapFromTo(x, a, b, c, d):
   y = (x - a) / (b - a) * (d - c) + c
   return y

def handle_pressure(unused_addr, args):
    try:
        logger.info(f'[{args}]')
        pwm.setServoPulse(0, int(mapFromTo(args, -15000, 15000, 500, 2500)))
    except ValueError as e:
        logger.error(e)
        
if __name__ == "__main__":
    pwm = PCA9685(0x40, debug=False)
    pwm.setPWMFreq(50)

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="10.0.1.58", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=10003, help="The port to listen on")
    args = parser.parse_args()
    
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/pressure", handle_pressure)
    
    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    logger.info(f'Serving on {server.server_address}')
    server.serve_forever()
    
 
