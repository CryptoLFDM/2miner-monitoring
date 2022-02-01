import orchestrator
import logging


async def do_async_req(session, url, wallet=None):
    async with session.get(url) as resp:
        r = await resp.json()
        if wallet is not None:
            r['wallet'] = wallet
        return r


def get_rig_info(rig_name):
    for rig in orchestrator.config['rig']:
        if rig['rig_name'] == rig_name:
            return rig
    logging.info("No rig found with name {}".format(rig_name))
    return None


def get_gpus(rig_name):
    rig = get_rig_info(rig_name)
    if rig is None:
        return ['No_GPU_FOUND']
    cards_list = []
    for card in rig['cards']:
        cards_list.append(card)
    return cards_list


def get_owners(rig_name):
    rig = get_rig_info(rig_name)
    if rig is None:
        return {'Name': 'unknown', 'parts': 0}
    owners = {}
    for owner in rig['owners']:
        owners['name'] = owner['name']
        owners['part'] = owner['ratio']
    return owners
