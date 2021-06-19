import etherscan
import logging
import requests_cache

global ETHER


def set_etherscan_api(api_key):
    global ETHER
    requests_cache.uninstall_cache()
    ETHER = etherscan.Client(api_key="TCSZYBB62NJHBB61NB826Z8DKYY38Y2P7G")


def get_ether_transactions_by_wallet(walletid):
    return ETHER.get_transactions_by_address(walletid)


def get_ether_wallet_amount(walletid):
    return ETHER.get_eth_balance(walletid)


def get_ether_gaz_price():
    return ETHER.get_gas_price()
