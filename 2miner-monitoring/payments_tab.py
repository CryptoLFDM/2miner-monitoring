from datetime import datetime
import pytz
from cluster_es import write_to_elasticsearch_index, delete_index_elasticsearch
import orchestrator


def write_payments(item):
    delete_index_elasticsearch('payments')
    for payment in item:        
        payment_raw = {
            "amount": payment['amount'] * orchestrator.gas_factor,
            "tx": payment['tx'],
            "txFee": payment['txFee'],
            "@timestamp": datetime.fromtimestamp(payment['timestamp'], pytz.UTC).isoformat(),
            "walletid": orchestrator.config['wallet']
        }
        write_to_elasticsearch_index('payments', payment_raw)


def harvest_payments_tab(payments):
    write_payments(payments)
