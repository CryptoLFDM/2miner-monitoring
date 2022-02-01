import logging
import orchestrator
import datetime

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from ssl import create_default_context

es = None


def transform_to_es_index(index_name, value):
    bulk_item = {
        "_index": index_name,
        "_source": value
    }
    return bulk_item


# async def get_block():
#     query = await get_query('pool-operator-blocks_win', 'blocks_win')
#     bulk_items = []
#     conn = await asyncpg.connect(user=cfg['postgres_user'], password=cfg['postgres_password'],
#                                  database=cfg['postgres_database'], host=cfg['postgres_host'])
#     values = await conn.fetch(query)
#     for value in values:
#         bulk_item = transform_to_es_index("pool-operator-blocks_win", value, 'coin_added_from_pg')
#         bulk_items.append(bulk_item)
#     await bulk_to_es(bulk_items)
#     await conn.close()


async def bulk_to_es(bulk_item):
    #await es_connection()
    try:
        logging.debug(await async_bulk(es, bulk_item))
    except Exception as e:
        logging.error('{}'.format(e))


async def es_write(index, body):
    pass

# async def es_write(index, body):
#     if len(body) == 0:
#         # TODO: add a better check if body is empty to avoid es co for nothing
#         logging.warning('Write on {} aborted, body is empty'.format(index))
#         return
#     now = datetime.datetime.now()
#     d1 = now.strftime("%Y.%m.%d")
#     index_name = '{}-{}-{}'.format(orchestrator.config['elasticsearch_user'], index, d1)
#     try:
#         logging.debug(await es.index(index=index_name, body=body))
#     except Exception as e:
#         logging.error('{}'.format(e))

async def es_delete(index):
    pass


# async def es_delete(index):
#     index_name = '{}-{}-2miners-monitoring'.format(orchestrator.config['elasticsearch_user'], index)
#     try:
#         await es.indices.delete(index=index_name, ignore=[400, 404])
#     except Exception as e:
#         logging.error('{}'.format(e))


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
    logging.debug(await es.info())
