import logging
from orchestrator import main_loop
import yaml
import click


def set_log_lvl(log_lvl):
    if log_lvl == 'INFO':
        return logging.INFO
    elif log_lvl == 'ERROR':
        return logging.ERROR
    elif log_lvl == 'WARNING':
        return logging.WARNING
    return logging.debug


@click.command()
@click.option('--config_file', '-c', default='../sample/config.yaml')
def main(config_file):
    click.echo("{}".format(config_file))
    with open(config_file, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=set_log_lvl(config['log_level']))
            logging.info('Conf file {} succefully loaded'.format(config_file))
        except Exception as e:
            logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=set_log_lvl('INFO'))
            logging.error('Unable to open file {}, error: {}'.format(config_file, e))
            quit()
    main_loop(config)


if __name__ == '__main__':
    main()
