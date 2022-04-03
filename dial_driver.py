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

import time

from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc import udp_client
from pythonosc import osc_message_builder
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


def loop_needle():
    pwm.set_servo_pulse(15, 10)
    return


def handle_pressure(unused_addr, args):
    """ Handle the update from the pressure sensor """
    try:
        logger.info(f'[{int(args)}]')
        #pwm.set_servo_pulse(15, int(map_from_to(args, -5000, 12000, 500, 2500)))
        pwm.set_servo_pulse(15, int(args))
    except ValueError as e:
        logger.error(e)


async def loop():
    tick = 1
    while True:
        msg = osc_message_builder.OscMessageBuilder(address="/tick")
        msg.add_arg(tick)
        built = msg.build()
        mobile_client.send(built)
        tick = tick + 1
        await asyncio.sleep(1)


async def init_main(args, dispatcher):
    server = AsyncIOOSCUDPServer((args.ip, args.port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()

    await loop()

    transport.close()


if __name__ == "__main__":
    pwm = PCA9685(logger=logger)
    pwm.set_pwm_freq(50)
    for i in range(2):
        pwm.set_servo_pulse(0, 500)
        time.sleep(0.1)
        for i in range(500, 2500, 10):
            time.sleep(0.01)
            pwm.set_servo_pulse(0, i)

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="192.168.1.4", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=8888, help="The port to listen on")
    parser.add_argument('--mobile_ip', default='192.168.1.5',
                        help='The ip of the mobile osc display')
    parser.add_argument('--mobile_port', type=int, default=8888,
                        help='The port the mobile osc display is listening on')
    args = parser.parse_args()

    mobile_client = udp_client.UDPClient(args.mobile_ip, args.mobile_port)

    dispatcher = Dispatcher()
    dispatcher.map("/pressure", handle_pressure)

    logger.info(f'Serving on {args.ip}')

    asyncio.run(init_main(args, dispatcher))
