import asyncio
import aiohttp
import http3
import logging
from utils import do_async_req


async def eth_price():
    async with aiohttp.ClientSession() as session:
        tasks = []
        url = 'https://blockchain.info/ticker?base=ETH'
        tasks.append(asyncio.ensure_future(do_async_req(session, url)))
        price = await asyncio.gather(*tasks)
        await session.close()
    return price