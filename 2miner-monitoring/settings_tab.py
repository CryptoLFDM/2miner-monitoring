from cluster_es import es_write
import orchestrator


async def write_settings(item, walletid):
    settings = {
        "@timestamp": orchestrator.clock_time,
        "allowedMaxPayout": item['allowedMaxPayout'] * orchestrator.gas_factor,
        "allowedMinPayout": item['allowedMinPayout'] * orchestrator.gas_factor,
        "defaultMinPayout": item['defaultMinPayout'] * orchestrator.gas_factor,
        "minPayout": item['minPayout'] * orchestrator.gas_factor,
        "walletid": walletid
    }
    await es_write('settings', settings)


async def harvest_settings_tab(settings, walletid):
    await write_settings(settings, walletid)
