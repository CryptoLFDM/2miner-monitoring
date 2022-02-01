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
from cluster_es import es_connection

config = None
es = None
clock_time = None
market_price = None
factor = 0.000001
ether_factor = 0.000000000000000001
gas_factor = 0.000000001


async def clock_pause():
    await asyncio.sleep(config['interval'] * 60)


async def process_miner(wallet):
    start = datetime.now()
    logging.warning('processing of {} at {}'.format(wallet, start))
#    try:
    result = await get_miner(wallet)
    await harvest_general_tab(result)
    await harvest_settings_tab(result['config'])
    await harvest_payments_tab(result['payments'])
    await harvest_rewards_tab(result)
    stop = datetime.now()
    duration = stop - start
    logging.warning('end of {} at {}. Duration : '.format(wallet, stop, duration.total_seconds()))
    del result
#    except Exception as e:
#        logging.error('error during orchestrator: {}'.format(e))


def main_loop(cfg):
    global config
    config = cfg
    set_etherscan_api(config['api_token_etherscan'])
    loop = asyncio.get_event_loop()
    logging.info("Bridge open, interval is {} min".format(config['interval']))
    iterator = 0
    es_connection()
    while True:
        #all_miners = loop.run_until_complete(get_all_miners())
        main_loop_clock = datetime.now()
        try:
            global market_price
            market_price = loop.run_until_complete(eth_price())
        except Exception as e:
            logging.error('unable to get ETH price with error {}'.format(e))
        miner = 0
        #for value in all_miners['miners']:
        for value in config['adresse']:
            if value.startswith('0x'):
                logging.warning("start of miners loops at {}. Iterator = {}, miner = {}".format(main_loop_clock, iterator, miner))
                global clock_time
                clock_time = datetime.fromtimestamp(time.time(), pytz.UTC).isoformat(),
                loop.run_until_complete(process_miner(value))
                logging.warning("end of miners loops at {}. Iterator = {}, miner = {}".format(main_loop_clock, iterator, miner))
                miner = miner + 1
            else:
                logging.warning("skipping {}, NANO or BTC not yet implemented".format(value))

        iterator = iterator + 1

        # logging.info("{} min is gonna pass".format(config['interval']))
        # loop.run_until_complete(clock_pause())
        # logging.info("{} min has been waited".format(config['interval']))
