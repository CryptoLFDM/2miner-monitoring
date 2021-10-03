from cluster_es import write_to_elasticsearch_index
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
    write_to_elasticsearch_index('settings', settings)


def harvest_settings_tab(settings):
    write_settings(settings)
