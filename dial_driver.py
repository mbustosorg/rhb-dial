"""
    Copyright (C) 2020 Mauricio Bustos (m@bustos.org)
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

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
   """ Map coordinates """
   y = (x - a) / (b - a) * (d - c) + c
   return y

def handle_pressure(unused_addr, args):
   """ Handle the update from the pressure sensor """
   try:
      logger.info(f'[{args}]')
      pwm.setServoPulse(15, int(mapFromTo(args, -15000, 15000, 500, 2500)))
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
   
 
