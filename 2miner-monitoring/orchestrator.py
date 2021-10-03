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
    while True:
        currency = requests.get('https://blockchain.info/ticker?base=ETH'.format(config['wallet']))
        global market_price
        market_price = currency.json()
        r = requests.get('https://eth.2miners.com/api/accounts/{}'.format(config['wallet']))
        logging.debug('{} {}'.format(r.status_code, r.url))
        global clock_time
        clock_time = datetime.fromtimestamp(time.time(), pytz.UTC).isoformat(),
        result = r.json()
        r.close()
        harvest_general_tab(result)
        harvest_settings_tab(result['config'])
        harvest_payments_tab(result['payments'])
        harvest_rewards_tab(result)
        time.sleep(60)
