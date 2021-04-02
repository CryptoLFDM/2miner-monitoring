import etherscan

global ether


def set_etherscan_api(api_key):
    global ether
    ether = etherscan.Client(
        api_key=api_key,
        cache_expire_after=5,
    )


def get_ether_transactions_by_wallet(walletid):
    return ether.get_transactions_by_address(walletid)


def get_ether_wallet_amount(walletid):
    return ether.get_eth_balance(walletid)


def get_ether_gaz_price():
    return ether.get_gas_price()
