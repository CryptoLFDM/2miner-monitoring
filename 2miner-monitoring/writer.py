import sys

import requests
from datetime import datetime
from elasticsearch import Elasticsearch
import time
import pytz
import logging
from etherscan_api import get_ether_transactions_by_wallet, get_ether_wallet_amount, get_ether_gaz_price
from ssl import create_default_context


factor = 0.000001
bounty_factor = 0.000000001
ether_factor = 0.000000000000000001
gas_factor = 0.000000001

global es
global cfg


def get_rig_info(rig_name):
    for rig in cfg['rig']:
        if rig['rig_name'] == rig_name:
            return rig
    return None


def get_gpus(rig_name):
    rig = get_rig_info(rig_name)
    if rig is None:
        return ['No_GPU_FOUND']
    cards_list = []
    for card in rig['cards']:
        cards_list.append(card)
    return cards_list


def get_owners(rig_name):
    rig = get_rig_info(rig_name)
    if rig is None:
        return {'Name': 'unknown', 'parts': 0}
    owners = {}
    for owner in rig['owners']:
        owners['name'] = owner['name']
        owners['part'] = owner['ratio']
    return owners


def write_to_elasticsearch_index(index, body):
    index_name = '{}-{}-2miners-monitoring'.format(cfg['elasticsearch_user'], index)
    try:
        logging.debug(es.index(index=index_name, body=body))
    except Exception as e:
        logging.error('unable to write on elasticsearch, error is {}'.format(e))


def delete_index_elasticsearch(index):
    index_name = '{}-{}-2miners-monitoring'.format(cfg['elasticsearch_user'], index)
    try:
        logging.debug(es.indices.delete(index='transaction', ignore=[400, 404]))
    except Exception as e:
        logging.error('Unable to delete index {}, error is {}'.format(index_name, e))


def write_pay(item, clock_time):
    delete_index_elasticsearch(index='bounty')
    for pay in item:

        bounty = {
            "amount": pay['amount'] * bounty_factor,
            "@timestamp": clock_time,
            "walletid": cfg['wallet']
        }
        write_to_elasticsearch_index('bounty', bounty)


def write_transactions(walletid):
    delete_index_elasticsearch(index='transaction')
    transactions = get_ether_transactions_by_wallet(walletid)
    for transaction in transactions:
        writable_transaction = {
            "@timestamp": datetime.fromtimestamp(transaction['timestamp'], pytz.UTC).isoformat(),
            "value": transaction['value'] * ether_factor,
            "gas": transaction['gas'],
            "to": transaction['to'],
            "from": transaction['from'],
            "gas_price": transaction['gas_price'],
            "gas_used": transaction['gas_used'],
            "is_error": transaction['is_error'],
            "walletid": cfg['wallet']
        }
        write_to_elasticsearch_index('transaction', writable_transaction)


def write_gas(clock_time):
    gas = {
        "@timestamp": clock_time,
        "gas_price": get_ether_gaz_price() * gas_factor,
        "walletid": cfg['wallet']
    }
    logging.info(gas)
    write_to_elasticsearch_index('gas', gas)


def write_wallet(walletid, market_price, clock_time):
    wallet = {
        "ether_amount": get_ether_wallet_amount(walletid) * ether_factor,
        "ether_current_price": market_price['EUR']['last'],
        "@timestamp": clock_time,
        "walletid": cfg['wallet']
    }
    write_to_elasticsearch_index('wallet', wallet)


def write_worker(item, clock_time):
    for miner in item:
        farm = {
            "Miner": miner,
            "Global_hashrate": item[miner]['hr'] * factor,
            "offline": item[miner]['offline'],
            "@timestamp": clock_time,
            "owner": get_owners(miner),
            "gpu": get_gpus(miner),
            "walletid": cfg['wallet']
        }
        write_to_elasticsearch_index('miner', farm)


def write_global(item, market_price, clock_time):
    global_info = {
        "Global_hashrate": item['currentHashrate'] * factor,
        "paiement": item['paymentsTotal'],
        "@timestamp": clock_time,
        "workersOnline": item['workersOnline'],
        "workersOffline": item['workersOffline'],
        "workersTotal": item['workersTotal'],
        "eth_price": market_price['EUR']['last'],
        "walletid": cfg['wallet']
    }
    write_to_elasticsearch_index('2miner', global_info)


def write_stats(item, market_price, clock_time):
    bfound = 0
    # if item['blocksFound'] is not None: TODO: why that does not work
    #    bfound = item['blocksFound']
    stats = {
        "balance": item['balance'] * bounty_factor,
        "blocksFound": bfound,
        "immature": item['immature'],
        "lastShare": item['lastShare'],
        "paid": item['paid'] * bounty_factor,
        "@timestamp": clock_time,
        "pending": item['pending'],
        "eth_price": market_price['EUR']['last'],
        "walletid": cfg['wallet']
    }
    write_to_elasticsearch_index('eth_stats', stats)


def elasticsearch_connection():
    # Connect to the elastic cluster
    global es
    context = create_default_context(cafile=cfg['ca_path'])
    try:
        es = Elasticsearch(
            [cfg['elasticsearch_host'] + ":9201", cfg['elasticsearch_host'] + ":9202", cfg['elasticsearch_host'] + ":9203"],
            http_auth=(cfg['elasticsearch_user'], cfg['elasticsearch_password']),
            scheme="https",
            port=cfg['elasticsearch_port'],
            ssl_context=context
        )
        logging.info(es.info())
    except Exception as e:
        logging.error('Unable to connect to es cluster, error is {}'.format(e))
        quit()


def elasticsearch_entry_point(config):
    global cfg
    
    cfg = config
    elasticsearch_connection()
    while True:
        try:
            currency = requests.get('https://blockchain.info/ticker?base=ETH'.format(cfg['wallet']))
            logging.info('{} {}'.format(currency.status_code, currency.url))
            market_price = currency.json()

            r = requests.get('https://eth.2miners.com/api/accounts/{}'.format(cfg['wallet']))
            logging.info('{} {}'.format(r.status_code, r.url))
            clock_time = datetime.fromtimestamp(time.time(), pytz.UTC).isoformat(),
            result = r.json()
            write_global(result, market_price, clock_time)
            write_worker(result['workers'], clock_time)
            write_stats(result['stats'], market_price, clock_time)
            write_wallet(cfg['wallet'], market_price, clock_time)
            write_pay(result['payments'], clock_time)
            write_transactions(cfg['wallet'])
            write_gas(clock_time)
            r.close()
            time.sleep(60)
        except Exception as e:
            logging.error('an error has been catch, error : {}'.format(e))
