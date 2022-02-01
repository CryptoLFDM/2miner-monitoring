import http3
import logging


async def eth_price():
    client = http3.AsyncClient()
    try:
        r = await client.get('https://blockchain.info/ticker?base=ETH')
        logging.debug('{} {}'.format(r.status_code, r.url))
        result = r.json()
        await client.close()
        return result
    except Exception as e:
        await client.close()
        logging.error('Unable to get eth price from blockchain.info: {}'.format(e))