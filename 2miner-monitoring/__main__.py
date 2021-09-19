import cli.app
import logging
from writer import elasticsearch_entry_point
from etherscan_api import set_etherscan_api
import yaml

config = None


def set_log_lvl(log_lvl):
    if log_lvl == 'INFO':
        return logging.INFO
    return logging.debug


@cli.app.CommandLineApp(name='2miner-monitoring')
def main(app):
    global config
    with open(app.param.config, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            print(config)
        except:
            pass
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=set_log_lvl(config['log_level']))
    set_etherscan_api(config['api_token_etherscan'])
    elasticsearch_entry_point(config)


main.add_param("-c", "--config", type=str, help="config file path", default="sample/config.yaml")

if __name__ == '__main__':
    main.run()
