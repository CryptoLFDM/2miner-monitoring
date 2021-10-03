from elasticsearch import Elasticsearch
from ssl import create_default_context
import logging
import orchestrator
es = None


def write_to_elasticsearch_index(index, body):
    index_name = '{}-{}-2miners-monitoring'.format(orchestrator.config['elasticsearch_user'], index)
    try:
        logging.debug(es.index(index=index_name, body=body))
    except Exception as e:
        logging.error('unable to write on elasticsearch, error is {}'.format(e))


def delete_index_elasticsearch(index):
    index_name = '{}-{}-2miners-monitoring'.format(orchestrator.config['elasticsearch_user'], index)
    try:
        logging.debug(es.indices.delete(index='transaction', ignore=[400, 403, 404]))
    except Exception as e:
        logging.error('Unable to delete index {}, error is {}'.format(index_name, e))


def elasticsearch_connection():
    # Connect to the elastic cluster
    context = create_default_context(cafile=orchestrator.config['ca_path'])
    try:
        global es
        es = Elasticsearch(
            [orchestrator.config['elasticsearch_host'] + ":9201", orchestrator.config['elasticsearch_host'] + ":9202", orchestrator.config['elasticsearch_host'] + ":9203"],
            http_auth=(orchestrator.config['elasticsearch_user'], orchestrator.config['elasticsearch_password']),
            scheme="https",
            port=orchestrator.config['elasticsearch_port'],
            ssl_context=context
        )
        logging.debug(es.info())
    except Exception as e:
        logging.error('Unable to connect to es cluster, error is {}'.format(e))
        quit()
