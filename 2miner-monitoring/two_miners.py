import logging
import http3


async def get_all_miners():
    client = http3.AsyncClient()
    try:
        r = await client.get('https://eth.2miners.com/api/miners')
        logging.debug('{} {}'.format(r.status_code, r.url))
        result = r.json()
        await client.close()
        return result
    except Exception as e:
        await client.close()
        logging.error('Unable to get miners from 2miners: {}'.format(e))


async def get_miner(wallet):
    client = http3.AsyncClient()
    try:
        r = await client.get('https://eth.2miners.com/api/accounts/{}'.format(wallet))
        logging.debug('{} {}'.format(r.status_code, r.url))
        result = r.json()
        await client.close()
        return result
    except Exception as e:
        await client.close()
        logging.error('Unable to get miners from 2miners: {}'.format(e))