import logging
from datetime import datetime
import time
import pytz
import requests


def get_all_miner():
    try:
        r = requests.get('https://eth.2miners.com/api/miners')
        logging.debug('{} {}'.format(r.status_code, r.url))
        result = r.json()
        return result
    except Exception as e:
        logging.error('error during orchestrator: {}'.format(e))