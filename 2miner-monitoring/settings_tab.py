from cluster_es import es_write
import orchestrator


def write_settings(item):
    settings = {
        "@timestamp": orchestrator.clock_time,
        "allowedMaxPayout": item['allowedMaxPayout'] * orchestrator.gas_factor,
        "allowedMinPayout": item['allowedMinPayout'] * orchestrator.gas_factor,
        "defaultMinPayout": item['defaultMinPayout'] * orchestrator.gas_factor,
        "minPayout": item['minPayout'] * orchestrator.gas_factor,
        "walletid": orchestrator.config['wallet']
    }
    es_write('settings', settings)


def harvest_settings_tab(settings):
    write_settings(settings)
