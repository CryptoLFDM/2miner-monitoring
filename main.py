import requests
from datetime import datetime
from elasticsearch import Elasticsearch
import time
import pytz
import cli.app

factor = 0.000001
bounty_factor = 0.000000001


def write_pay(item, readable, es):
    for pay in item:
        bounty = {
            "Amount": pay['amount'] * bounty_factor,
            "pay_date": pay['timestamp'],
            "Date": readable
        }
        es.index(index='bounty', body=bounty)


def write_worker(item, readable, es):
    for miner in item:
        farm = {
            "Miner": miner,
            "Global_hashrate": item[miner]['hr'] * factor,
            "offline": item[miner]['offline'],
            "Date": readable
        }
        es.index(index='miner', body=farm)


def write_global(item, readable, es):
    global_info = {
        "Global_hashrate": item['currentHashrate'] * factor,
        "paiement": item['paymentsTotal'],
        "Date": readable,
        "workersOnline": item['workersOnline'],
        "workersOffline": item['workersOffline'],
        "workersTotal": item['workersTotal']
    }
    es.index(index='2miner', body=global_info)


def es_entry_point(walletid):
    # Connect to the elastic cluster
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    r = requests.get('https://eth.2miners.com/api/accounts/{}'.format(walletid))
    result = r.json()

    while True:
        readable = datetime.fromtimestamp(result['updatedAt'] * 0.001, pytz.UTC).isoformat()
        write_global(result, readable, es)
        write_pay(result['payments'], readable, es)
        write_worker(result['workers'], readable, es)
        time.sleep(30)


@cli.app.CommandLineApp(name='2miner-monitoring')
def main(app):
    es_entry_point(app.params.wallet)


# Build the options of the CLI
main.add_param("-w", "--wallet", type=str, help="wallet id", required=True)

if __name__ == '__main__':
    main.run()
