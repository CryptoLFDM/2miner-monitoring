import asyncio
from datetime import datetime
import logging
import time
import aiohttp
from utils import do_async_req


async def harvest_miners(iterator, all_miners):
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = []
        iterator_miner = 0
        for wallet in all_miners:
            loop_start_time = time.time()
            logging.warning(
                "collecting {} at {}. Iterator = {}, miner = {}".format(wallet, datetime.now(), iterator, iterator_miner))
            url = f'https://eth.2miners.com/api/accounts/{wallet}'
            tasks.append(asyncio.ensure_future(do_async_req(session, url, wallet)))
            logging.warning(
                "collected {} at {}. Iterator = {}, miner = {}, duration = {}, loop_duration = {}".format(wallet, datetime.now(), iterator,
                                                                                         iterator_miner, time.time() - start_time,  time.time() - loop_start_time))
            iterator_miner = iterator_miner + 1
        miners = await asyncio.gather(*tasks)
    return miners


async def harvest_miners_adresses():
    async with aiohttp.ClientSession() as session:
        tasks = []
        eth_adresses = []
        url = 'https://eth.2miners.com/api/miners'
        tasks.append(asyncio.ensure_future(do_async_req(session, url)))
        miners = await asyncio.gather(*tasks)
        for adress in miners[0]['miners']:
            if adress.startswith('0x'):
                eth_adresses.append(adress)
            else:
                logging.warning("skipping {}, NANO or BTC not yet implemented".format(adress))
    return eth_adresses

