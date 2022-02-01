from cluster_es import es_write, es_delete
import orchestrator
from datetime import datetime
import pytz


async def write_rewards(item):
    await es_delete('rewards')
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
        await es_write('rewards', reward_raw)


async def write_sumrewards(item):
    for sumreward in item:
        sumreward_raw = {
            "inverval": sumreward['inverval'],
            "reward": sumreward['reward'] * orchestrator.gas_factor,
            "numreward": sumreward['numreward'],
            "name": sumreward['name'],
            "@timestamp": orchestrator.clock_time,
            "walletid": orchestrator.config['wallet']
        }
        await es_write('sumrewards', sumreward_raw)


async def harvest_rewards_tab(result):
    await write_rewards(result['rewards'])
    await write_sumrewards(result['sumrewards'])
