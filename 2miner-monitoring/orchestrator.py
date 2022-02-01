import logging

import aiohttp
import asyncio
import pytz
from datetime import datetime
import time

from general_tab import harvest_general_tab
from settings_tab import harvest_settings_tab
from payments_tab import harvest_payments_tab
from rewards_tab import harvest_rewards_tab
from etherscan_api import set_etherscan_api
from two_miners import harvest_miners_adresses, harvest_miners
from third_app import eth_price
from cluster_es import es_connection

config = None
es = None
clock_time = None
market_price = None
factor = 0.000001
ether_factor = 0.000000000000000001
gas_factor = 0.000000001


async def process_miner(miner_info):
    start = time.time()
    logging.warning('processing of {} at {}'.format(miner_info['wallet'], datetime.now()))
    await harvest_general_tab(miner_info)
    await harvest_settings_tab(miner_info['config'], miner_info['wallet'])
    await harvest_payments_tab(miner_info['payments'], miner_info['wallet'])
    await harvest_rewards_tab(miner_info)
    logging.warning('end of {} at {}. Duration : {}'.format(miner_info['wallet'], datetime.now(), time.time() - start))


def main_loop(cfg):
    global config
    config = cfg
    set_etherscan_api(config['api_token_etherscan'])
    iterator = 0
    asyncio.run(es_connection())
    global market_price
    market_price = asyncio.run(eth_price())
    while True:
        try:
            if config['include_all_miners'] == "True":
                all_miners = asyncio.run(harvest_miners_adresses())
            else:
                all_miners = config['adress']
            if datetime.now().second == 0:  # update ETH price once per minute only
                market_price = asyncio.run(eth_price())
            global clock_time
            clock_time = datetime.fromtimestamp(time.time(), pytz.UTC).isoformat()
            miners = asyncio.run(harvest_miners(iterator, all_miners))
            for miner in miners:
                asyncio.run(process_miner(miner))
            iterator = iterator + 1
        except:
            pass

