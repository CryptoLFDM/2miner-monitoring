import requests
from datetime import datetime
from elasticsearch import Elasticsearch
import time
import pytz
import logging

factor = 0.000001
bounty_factor = 0.000000001


def write_pay(item, readable, es):
    for pay in item:
        bounty = {
            "Amount": pay['amount'] * bounty_factor,
            "pay_date": pay['timestamp'],
            "Date": readable
        }
        logging.debug(es.index(index='bounty', body=bounty))


def write_worker(item, readable, es):
    for miner in item:
        farm = {
            "Miner": miner,
            "Global_hashrate": item[miner]['hr'] * factor,
            "offline": item[miner]['offline'],
            "Date": readable
        }
        logging.debug(es.index(index='miner', body=farm))


def write_global(item, readable, es, market_price):
    global_info = {
        "Global_hashrate": item['currentHashrate'] * factor,
        "paiement": item['paymentsTotal'],
        "Date": readable,
        "workersOnline": item['workersOnline'],
        "workersOffline": item['workersOffline'],
        "workersTotal": item['workersTotal'],
        "eth_price": market_price['EUR']['last']
    }
    logging.debug(es.index(index='2miner', body=global_info))


def write_stats(item, readable, es, market_price):
    bfound = 0
    #if item['blocksFound'] is not None: TODO: why that does not work
    #    bfound = item['blocksFound']
    stats = {
        "balance": item['balance'] * bounty_factor,
        "blocksFound": bfound,
        "immature": item['immature'],
        "lastShare": item['lastShare'],
        "paid": item['paid'] * bounty_factor,
        "Date": readable,
        "pending": item['pending'],
        "eth_price": market_price['EUR']['last']
    }
    logging.debug(es.index(index='eth_stats', body=stats))


def es_entry_point(walletid, user, password, es_host, es_port):
    # Connect to the elastic cluster
    es = Elasticsearch(
        [es_host],
        http_auth=(user, password),
        port=es_port,
    )
    logging.info(es.info())

    while True:
        currency = requests.get('https://blockchain.info/ticker?base=ETH'.format(walletid))
        logging.info('{} {}'.format(currency.status_code, currency.url))
        market_price = currency.json()

        r = requests.get('https://eth.2miners.com/api/accounts/{}'.format(walletid))
        logging.info('{} {}'.format(r.status_code, r.url))
        result = r.json()
        readable = datetime.fromtimestamp(result['updatedAt'] * 0.001, pytz.UTC).isoformat()
        write_global(result, readable, es, market_price)
        write_pay(result['payments'], readable, es)
        write_worker(result['workers'], readable, es)
        write_stats(result['stats'], readable, es, market_price)
        time.sleep(10)
