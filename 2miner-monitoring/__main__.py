import logging
from writer import elasticsearch_entry_point
from etherscan_api import set_etherscan_api
import yaml
import click


config = None


def set_log_lvl(log_lvl):
    if log_lvl == 'INFO':
        return logging.INFO
    return logging.debug


@click.command()
@click.option('--config_file', '-c', default='../sample/config.yaml')
def main(config_file):
    click.echo("{}".format(config_file))

    global config
    with open(config_file, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=set_log_lvl(config['log_level']))
            logging.info('Conf file {} succefully loaded'.format(config_file))
        except Exception as e:
            logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=set_log_lvl('INFO'))
            logging.error('Unable to open file {}, error: {}'.format(config_file, e))
            quit()
    set_etherscan_api(config['api_token_etherscan'])
    elasticsearch_entry_point(config)


if __name__ == '__main__':
    main()
