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

import piglow

from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio

from PCA9685 import PCA9685

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('IMU')
logger.setLevel(logging.INFO)

last_change = 0


def map_from_to(x, a, b, c, d):
    """ Map coordinates """
    y = (x - a) / (b - a) * (d - c) + c
    return y


def handle_pressure(unused_addr, args):
    """ Handle the update from the pressure sensor """
    try:
        logger.info(f'[{args}]')
        pwm.set_servo_pulse(15, int(map_from_to(args, -5000, 12000, 0, 3000)))
    except ValueError as e:
        logger.error(e)


async def loop():
    while True:
        await asyncio.sleep(1)


"""
   last_change = 0
   for i in range(10):
      if last_change == 0:
         last_change = 1
         piglow.red(64)
      else:
         last_change = 0
         piglow.red(0)
      piglow.show()
      print(f"Loop {i}")
      await asyncio.sleep(1)
"""


async def init_main(args, dispatcher):
    server = AsyncIOOSCUDPServer((args.ip, args.port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()

    await loop()

    transport.close()


if __name__ == "__main__":
    pwm = PCA9685(logger=logger)
    pwm.set_pwm_freq(50)

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="10.0.1.32", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=10003, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = Dispatcher()
    dispatcher.map("/pressure", handle_pressure)

    logger.info(f'Serving on {args.ip}')

    asyncio.run(init_main(args, dispatcher))
