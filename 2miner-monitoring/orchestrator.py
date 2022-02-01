import logging
import http3
import asyncio
import pytz
from datetime import datetime
import time

from general_tab import harvest_general_tab
from settings_tab import harvest_settings_tab
from payments_tab import harvest_payments_tab
from rewards_tab import harvest_rewards_tab
from etherscan_api import set_etherscan_api
from two_miners import get_all_miners, get_miner
from third_app import eth_price

config = None
es = None
clock_time = None
market_price = None
factor = 0.000001
ether_factor = 0.000000000000000001
gas_factor = 0.000000001


async def clock_pause():
    await asyncio.sleep(config['interval'] * 60)


def main_loop(cfg):
    global config
    config = cfg
    set_etherscan_api(config['api_token_etherscan'])
    loop = asyncio.get_event_loop()
    logging.info("Bridge open, interval is {} min".format(config['interval']))
    while True:
        all_miners = loop.run_until_complete(get_all_miners())
        for value in all_miners['miners']:
            global clock_time
            clock_time = datetime.fromtimestamp(time.time(), pytz.UTC).isoformat(),
            try:
                global market_price
                market_price = loop.run_until_complete(eth_price())
            except Exception as e:
                logging.error('unable to get ETH price with error {}'.format(e))
            try:
                result = loop.run_until_complete(get_miner(value))
                loop.run_until_complete(harvest_general_tab(result))
                loop.run_until_complete(harvest_settings_tab(result['config']))
                loop.run_until_complete(harvest_payments_tab(result['payments']))
                loop.run_until_complete(harvest_rewards_tab(result))
                del result
            except Exception as e:
                logging.error('error during orchestrator: {}'.format(e))
        # logging.info("{} min is gonna pass".format(config['interval']))
        # loop.run_until_complete(clock_pause())
        # logging.info("{} min has been waited".format(config['interval']))

