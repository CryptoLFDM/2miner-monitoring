from datetime import datetime
import pytz
from cluster_es import es_write, es_delete
import orchestrator


async def write_payments(item):
    await es_delete('payments')
    for payment in item:
        payment_raw = {
            "amount": payment['amount'] * orchestrator.gas_factor,
            "tx": str(payment['tx']),
            "txFee": payment['txFee'] * orchestrator.gas_factor,
            "@timestamp": datetime.fromtimestamp(payment['timestamp'], pytz.UTC).isoformat(),
            "walletid": orchestrator.config['wallet']
        }
        await es_write('payments', payment_raw)


async def harvest_payments_tab(payments):
    await write_payments(payments)
