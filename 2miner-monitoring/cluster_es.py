import logging
import orchestrator
import datetime

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from ssl import create_default_context

es = None


async def bulk_to_es(bulk_item):
    await es_connection()
    try:
        logging.debug(await async_bulk(es, bulk_item))
    except Exception as e:
        logging.error('{}'.format(e))
    await es.close()


async def es_write(index, body):
    if len(body) == 0:
        # TODO: add a better check if body is empty to avoid es co for nothing
        logging.warning('Write on {} aborted, body is empty'.format(index))
        return
    now = datetime.datetime.now()
    d1 = now.strftime("%Y.%m.%d")
    index_name = '{}-{}-{}'.format(orchestrator.config['elasticsearch_user'], index, d1)
    await es_connection()
    try:
        logging.debug(await es.index(index=index_name, body=body))
    except Exception as e:
        logging.error('{}'.format(e))
    await es.close()


async def es_delete(index):
    index_name = '{}-{}-2miners-monitoring'.format(orchestrator.config['elasticsearch_user'], index)
    await es_connection()
    try:
        await es.indices.delete(index=index_name, ignore=[400, 404])
    except Exception as e:
        logging.error('{}'.format(e))
    await es.close()


async def es_connection():
    # Connect to the elastic cluster
    global es
    context = create_default_context(cafile=orchestrator.config['ca_path'])
    es = AsyncElasticsearch(
            hosts=orchestrator.config['elasticsearch_hosts'],
            http_auth=(orchestrator.config['elasticsearch_user'], orchestrator.config['elasticsearch_password']),
            scheme="https",
            port=orchestrator.config['elasticsearch_port'],
            ssl_context=context
        )
    logging.info(await es.info())
