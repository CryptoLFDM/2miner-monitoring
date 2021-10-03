from cluster_es import write_to_elasticsearch_index, delete_index_elasticsearch
import orchestrator
from datetime import datetime
import pytz


def write_rewards(item):
    delete_index_elasticsearch('rewards')
    for reward in item:
        reward_raw = {
            "blockheight": reward['blockheight'],
            "reward": reward['reward'] * orchestrator.gas_factor,
            "percent": reward['percent'],
            "immature": reward['immature'],
            "orphan": reward['orphan'],
            "uncle": reward['uncle'],
            "@timestamp": datetime.fromtimestamp(reward['timestamp'], pytz.UTC).isoformat(),
            "walletid": orchestrator.config['wallet']
        }
        write_to_elasticsearch_index('rewards', reward_raw)


def write_sumrewards(item):
    for sumreward in item:
        sumreward_raw = {
            "inverval": sumreward['inverval'],
            "reward": sumreward['reward'] * orchestrator.gas_factor,
            "numreward": sumreward['numreward'],
            "name": sumreward['name'],
            "@timestamp": orchestrator.clock_time,
            "walletid": orchestrator.config['wallet']
        }
        write_to_elasticsearch_index('sumrewards', sumreward_raw)


def harvest_rewards_tab(result):
    write_rewards(result['rewards'])
    write_sumrewards(result['sumrewards'])
