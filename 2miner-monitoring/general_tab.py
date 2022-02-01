from etherscan_api import get_ether_transactions_by_wallet, get_ether_wallet_amount, get_ether_gaz_price
from cluster_es import es_delete, es_write
from datetime import datetime
import pytz
import orchestrator
from utils import get_gpus, get_owners
import logging


async def write_pay(item, walletid):
    await es_delete(index='bounty')
    for pay in item:

        bounty = {
            "amount": pay['amount'] * orchestrator.gas_factor,
            "@timestamp": orchestrator.clock_time,
            "walletid": walletid
        }
        await es_write('bounty', bounty)


async def write_transactions(walletid):
    await es_delete(index='transaction')
    transactions = get_ether_transactions_by_wallet(walletid)
    for transaction in transactions:
        writable_transaction = {
            "@timestamp": datetime.fromtimestamp(transaction['timestamp'], pytz.UTC).isoformat(),
            "value": transaction['value'] * orchestrator.ether_factor,
            "gas": transaction['gas'],
            "to": transaction['to'],
            "from": transaction['from'],
            "gas_price": transaction['gas_price'],
            "gas_used": transaction['gas_used'] * orchestrator.gas_factor,
            "is_error": transaction['is_error'],
            "walletid": walletid
        }
        await es_write('transaction', writable_transaction)


async def write_gas(walletid):
    gas = {
        "@timestamp": orchestrator.clock_time,
        "gas_price": get_ether_gaz_price() * orchestrator.gas_factor,
        "walletid": walletid
    }
    await es_write('gas', gas)


async def write_wallet(walletid):
    wallet = {
        "ether_amount": get_ether_wallet_amount(walletid) * orchestrator.ether_factor,
        "ether_current_price": orchestrator.market_price['EUR']['last'],
        "@timestamp": orchestrator.clock_time,
        "walletid": walletid
    }
    await es_write('wallet', wallet)


async def write_worker(item, walletid):
    for miner in item:
        farm = {
            "Miner": miner,
            "lastBeat": datetime.fromtimestamp(item[miner]['lastBeat'], pytz.UTC).isoformat(),
            "sharesValid": item[miner]['sharesValid'],
            "sharesInvalid": item[miner]['sharesInvalid'],
            "sharesStale": item[miner]['sharesStale'],
            "Global_hashrate": item[miner]['hr'] * orchestrator.factor,
            "offline": item[miner]['offline'],
            "@timestamp": orchestrator.clock_time,
            "owner": get_owners(miner),
            "gpu": get_gpus(miner),
            "walletid": walletid
        }
        await es_write('miner', farm)


async def write_global(item):
    global_info = {
        "Global_hashrate": item['currentHashrate'] * orchestrator.factor,
        "paiement": item['paymentsTotal'],
        "@timestamp": orchestrator.clock_time,
        "workersOnline": item['workersOnline'],
        "workersOffline": item['workersOffline'],
        "workersTotal": item['workersTotal'],
        "currentLuck": float(item['currentLuck']),
        "24hreward": item['24hreward'] * orchestrator.gas_factor,
        "24hnumreward": item['24hnumreward'],
        "paymentsTotal": item['paymentsTotal'],
        "roundShares": item['roundShares'],
        "sharesInvalid": item['sharesInvalid'],
        "sharesStale": item['sharesStale'],
        "sharesValid": item['sharesValid'],
        "eth_price": orchestrator.market_price['EUR']['last'],
        "walletid": item['wallet']
    }
    await es_write('2miner', global_info)


async def write_stats(item, walletid):
    stats = {
        "balance": item['balance'] * orchestrator.gas_factor,
        "immature": item['immature'],
        "gas": item['gas'],
        "lastShare": datetime.fromtimestamp(item['lastShare'], pytz.UTC).isoformat(),
        "paid": item['paid'] * orchestrator.gas_factor,
        "@timestamp": orchestrator.clock_time,
        "pending": item['pending'],
        "eth_price": orchestrator.market_price['EUR']['last'],
        "walletid": walletid
    }
    await es_write('eth_stats', stats)


async def harvest_general_tab(general_tab, walletid):
    await write_global(general_tab)
    await write_worker(general_tab['workers'], general_tab['wallet'])
    await write_stats(general_tab['stats'], general_tab['wallet'])
    await write_wallet(general_tab['wallet'])
    await write_pay(general_tab['payments'], general_tab['wallet'])
    await write_transactions(general_tab['wallet'])
    await write_gas(general_tab['wallet'])
