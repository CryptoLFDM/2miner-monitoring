import logging
from datetime import datetime
import time
import pytz
import requests

from cluster_es import elasticsearch_connection
from general_tab import harvest_general_tab
from settings_tab import harvest_settings_tab
from payments_tab import harvest_payments_tab
from rewards_tab import harvest_rewards_tab
from etherscan_api import set_etherscan_api
from two_miners import get_all_miner

config = None
es = None
clock_time = None
market_price = None
factor = 0.000001
ether_factor = 0.000000000000000001
gas_factor = 0.000000001


def main_loop(cfg):
    global config
    config = cfg
    elasticsearch_connection()
    set_etherscan_api(config['api_token_etherscan'])
    url_eth_price = 'https://blockchain.info/ticker?base=ETH'
    result = get_all_miner()
    while True:
        for value in result['miners']:
            try:
                currency = requests.get(url_eth_price)
                global market_price
                market_price = currency.json()
            except Exception as e:
                logging.error('unable to get info from {}, with error {}'.format(url_eth_price, e))
            try:
                #r = requests.get('https://eth.2miners.com/api/accounts/{}'.format(config['wallet']))
                config['wallet'] = value
                r = requests.get('https://eth.2miners.com/api/accounts/{}'.format(config['wallet']))

                logging.debug('{} {}'.format(r.status_code, r.url))
                global clock_time
                clock_time = datetime.fromtimestamp(time.time(), pytz.UTC).isoformat(),
                result = r.json()
                harvest_general_tab(result)
                harvest_settings_tab(result['config'])
                harvest_payments_tab(result['payments'])
                harvest_rewards_tab(result)
                del result
                r.close()
            except Exception as e:
                logging.error('error during orchestrator: {}'.format(e))
        #time.sleep(60)
