import requests
from datetime import datetime
from elasticsearch import Elasticsearch
import time
import pytz
import logging
from etherscan_api import get_ether_transactions_by_wallet, get_ether_wallet_amount, get_ether_gaz_price

factor = 0.000001
bounty_factor = 0.000000001
ether_factor = 0.000000000000000001

Computers = {
    "Goudot": {
        "DESKTOP-T0SIC8V": "3060TI",
        "DESKTOP-S2F50O3": "3070",
        "DESKTOP-S9JBEI4": "3070",
    },
    "Rollet": {
        "DESKTOP-D14KDS8": "3070",
        "DESKTOP-0UVPTDO": "3070",
    }
}

global es

def get_computer_info(name):
    for owner in Computers:
        for computer in Computers[owner]:
            if computer == name:
                return [owner, Computers[owner][computer]]
    return ["no_owner", "no_gpu_record"]


def write_to_es(index, body):
    try:
        logging.debug(es.index(index=index, body=body))
    except:
        logging.error('unable to write on elasticsearch')


def write_pay(item):
    es.indices.delete(index='bounty', ignore=[400, 404])
    for pay in item:
        readable = datetime.fromtimestamp(pay['timestamp'], pytz.UTC).isoformat()
        bounty = {
            "amount": pay['amount'] * bounty_factor,
            "Date": readable,
        }
        write_to_es('bounty', bounty)


def write_transactions(walletid):
    es.indices.delete(index='transaction', ignore=[400, 404])
    transactions = get_ether_transactions_by_wallet(walletid)
    for transaction in transactions:
        readable = datetime.fromtimestamp(transaction['timestamp'], pytz.UTC).isoformat()
        writable_transaction = {
            "Date": readable,
            "value": transaction['value'] * ether_factor,
            "gas": transaction['gas'],
            "to": transaction['to'],
            "from": transaction['from'],
            "gas_price": transaction['gas_price'],
            "gas_used": transaction['gas_used'],
            "is_error": transaction['is_error']
        }
        write_to_es('transaction', writable_transaction)


def write_gas():
    gas = {
        "Date": datetime.fromtimestamp(time.time(), pytz.UTC).isoformat(),
        "gas_price": get_ether_gaz_price(),
    }
    write_to_es('gas', gas)


def write_wallet(readable, walletid, market_price):
    wallet = {
        "ether_amount": get_ether_wallet_amount(walletid),
        "ether_current_price": market_price['EUR']['last'],
        "Date": readable
    }
    write_to_es('wallet', wallet)


def write_worker(item, readable):
    for miner in item:
        computer_info = get_computer_info(miner)
        farm = {
            "Miner": miner,
            "Global_hashrate": item[miner]['hr'] * factor,
            "offline": item[miner]['offline'],
            "Date": readable,
            "owner" : computer_info[0],
            "gpu": computer_info[1],
        }
        write_to_es('miner', farm)


def write_global(item, readable, market_price):
    global_info = {
        "Global_hashrate": item['currentHashrate'] * factor,
        "paiement": item['paymentsTotal'],
        "Date": readable,
        "workersOnline": item['workersOnline'],
        "workersOffline": item['workersOffline'],
        "workersTotal": item['workersTotal'],
        "eth_price": market_price['EUR']['last']
    }
    write_to_es('2miner', global_info)


def write_stats(item, readable, market_price):
    bfound = 0
    # if item['blocksFound'] is not None: TODO: why that does not work
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
    write_to_es('eth_stats', stats)


def es_connection(user, password, es_host, es_port):
    # Connect to the elastic cluster
    global es
    es = Elasticsearch(
        [es_host],
        http_auth=(user, password),
        port=es_port,
    )
    logging.info(es.info())


def es_entry_point(walletid, user, password, es_host, es_port):
    es_connection(user, password, es_host, es_port)

    while True:
        try:
            currency = requests.get('https://blockchain.info/ticker?base=ETH'.format(walletid))
            logging.info('{} {}'.format(currency.status_code, currency.url))
            market_price = currency.json()

            r = requests.get('https://eth.2miners.com/api/accounts/{}'.format(walletid))
            logging.info('{} {}'.format(r.status_code, r.url))
            result = r.json()
            readable = datetime.fromtimestamp(result['updatedAt'] * 0.001, pytz.UTC).isoformat()
            write_global(result, readable, market_price)
            write_worker(result['workers'], readable)
            write_stats(result['stats'], readable, market_price)
            write_wallet(readable, walletid, market_price)
            write_pay(result['payments'])
            write_transactions(walletid)
            write_gas()
            r.close()
            time.sleep(10)
        except:
            pass
