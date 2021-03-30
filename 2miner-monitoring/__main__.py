import cli.app
import logging
from writer import es_entry_point


def set_log_lvl(log_lvl):
    if log_lvl == 'INFO':
        return logging.INFO
    return logging.debug


@cli.app.CommandLineApp(name='2miner-monitoring')
def main(app):
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=set_log_lvl(app.params.log_level))
    es_entry_point(app.params.wallet, app.params.user, app.params.password, app.params.es_host, app.params.es_port)


# Build the options of the CLI
main.add_param("-w", "--wallet", type=str, help="wallet id", required=True)
main.add_param("-u", "--user", type=str, help="user for es connection")
main.add_param("-p", "--password", type=str, help="password for es connection")
main.add_param("-eh", "--es_host", type=str, help="es hosts connection", default='localhost')
main.add_param("-ep", "--es_port", type=str, help="es port connection", default=9200)
main.add_param("-l", "--log_level", type=str, help="Log Level", default='INFO')

if __name__ == '__main__':
    main.run()
