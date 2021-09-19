import requests
from datetime import datetime
from elasticsearch import Elasticsearch
import time
import pytz
import logging
import json
from etherscan_api import get_ether_transactions_by_wallet, get_ether_wallet_amount, get_ether_gaz_price
from ssl import create_default_context


factor = 0.000001
bounty_factor = 0.000000001
ether_factor = 0.000000000000000001
gas_factor = 0.000000001

Computers = {
    "Goudot": {
        "DESKTOP-T0SIC8V": "3060TI",
        "DESKTOP-S2F50O3": "3070",
        "DESKTOP-1O4VIJC": "3070",
        "DESKTOP-6JI75RL": "3070",
        "DESKTOP-1R35NEA": "2070",
        "DESKTOP-160G6L9": "3090",
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

        bounty = {
            "amount": pay['amount'] * bounty_factor,
            "@timestamp": datetime.fromtimestamp(time.time(), pytz.UTC).isoformat(),
        }
        write_to_es('bounty', bounty)


def write_transactions(walletid):
    es.indices.delete(index='transaction', ignore=[400, 404])
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
            "is_error": transaction['is_error']
        }
        write_to_es('transaction', writable_transaction)


def write_gas():
    gas = {
        "@timestamp": datetime.fromtimestamp(time.time(), pytz.UTC).isoformat(),
        "gas_price": get_ether_gaz_price() * gas_factor,
    }
    logging.info(gas)
    write_to_es('gas', gas)


def write_wallet(walletid, market_price):
    wallet = {
        "ether_amount": get_ether_wallet_amount(walletid) * ether_factor,
        "ether_current_price": market_price['EUR']['last'],
        "@timestamp": datetime.fromtimestamp(time.time(), pytz.UTC).isoformat(),
    }
    write_to_es('wallet', wallet)


def write_worker(item):
    for miner in item:
        computer_info = get_computer_info(miner)
        farm = {
            "Miner": miner,
            "Global_hashrate": item[miner]['hr'] * factor,
            "offline": item[miner]['offline'],
            "@timestamp": datetime.fromtimestamp(time.time(), pytz.UTC).isoformat(),
            "owner": computer_info[0],
            "gpu": computer_info[1],
        }
        write_to_es('miner', farm)


def write_global(item, market_price):
    global_info = {
        "Global_hashrate": item['currentHashrate'] * factor,
        "paiement": item['paymentsTotal'],
        "@timestamp": datetime.fromtimestamp(time.time(), pytz.UTC).isoformat(),
        "workersOnline": item['workersOnline'],
        "workersOffline": item['workersOffline'],
        "workersTotal": item['workersTotal'],
        "eth_price": market_price['EUR']['last']
    }
    write_to_es('2miner', global_info)

def write_partial():
    es.indices.delete(index='partial', ignore=[400, 404])
    r = requests.get("https://api.frenchfarmers.net/partial/all")
    result = r.json()
    partial = []
    for raw in result:
        partial_raw = {
            "launcher_id": raw["launcher_id"],
            "difficulty": raw["difficulty"],
            "@timestamp": raw["timestamp"]
        }
        write_to_es('partial', partial_raw)
        partial.append(partial_raw)


def write_farmer():
    es.indices.delete(index='farmer', ignore=[400, 404])
    r = requests.get("https://api.frenchfarmers.net/farmer/all")
    result = r.json()
    farmer = []
    for raw in result:
        farmer_raw = {
            "launcher_id": raw["launcher_id"],
            "difficulty": raw["difficulty"],
            "points": raw["points"],
            "is_pool_member": raw["is_pool_member"],
            "@timestamp": datetime.fromtimestamp(time.time(), pytz.UTC).isoformat(),
        }
        write_to_es('farmer', farmer_raw)
        farmer.append(farmer_raw)

def write_stats(item, market_price):
    bfound = 0
    # if item['blocksFound'] is not None: TODO: why that does not work
    #    bfound = item['blocksFound']
    stats = {
        "balance": item['balance'] * bounty_factor,
        "blocksFound": bfound,
        "immature": item['immature'],
        "lastShare": item['lastShare'],
        "paid": item['paid'] * bounty_factor,
        "@timestamp": datetime.fromtimestamp(time.time(), pytz.UTC).isoformat(),
        "pending": item['pending'],
        "eth_price": market_price['EUR']['last']
    }
    write_to_es('eth_stats', stats)


def es_connection(user, password, es_host, es_port, cert):
    # Connect to the elastic cluster
    global es
    context = create_default_context(cafile=cert)
    es = Elasticsearch(
        [es_host + ":9201", es_host + ":9202", es_host + ":9203"],
        http_auth=(user, password),
        scheme="https",
        port=es_port,
        ssl_context=context,
    )
    logging.info(es.info())


def es_entry_point(walletid, user, password, es_host, es_port, cert):
    es_connection(user, password, es_host, es_port, cert)

    while True:
        try:
            currency = requests.get('https://blockchain.info/ticker?base=ETH'.format(walletid))
            logging.info('{} {}'.format(currency.status_code, currency.url))
            market_price = currency.json()

            r = requests.get('https://eth.2miners.com/api/accounts/{}'.format(walletid))
            logging.info('{} {}'.format(r.status_code, r.url))
            result = r.json()
            write_global(result, market_price)
            write_worker(result['workers'])
            write_stats(result['stats'], market_price)
            write_wallet(walletid, market_price)
            write_pay(result['payments'])
            write_transactions(walletid)
            write_gas()
#            write_farmer()
#            write_partial()
            r.close()
            time.sleep(60)
        except:
            pass
