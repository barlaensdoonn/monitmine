#!/usr/local/bin/python3
# decred via suprnova [MPOS] api
# 7/22/17
# updated 7/28/17

import bttrx
import minor
import requests

# NOTE: getusertransactions only returns last 100 transactions
actions = ['getuserstatus', 'getuserbalance', 'getdashboarddata', 'getusertransactions', 'getuserhashrate']
crrncys = ['btc', 'eth', 'zec', 'dcr', 'sia']
xchngs = ['usdt', 'btc']


def _construct_url(action):
    return 'https://dcr.suprnova.cc/index.php?page=api&action={}&api_key={}'.format(action, minor.suprnova_key)


def get_prices():
    btc_dcrd = bttrx.get_price('btc', 'dcr')
    usd_btc = bttrx.get_price('usdt', 'btc')
    usd_dcrd = btc_dcrd * usd_btc

    return {'price_btc': btc_dcrd, 'price_usd': usd_dcrd}


def get_balance():
    balance = 0
    r_balance = requests.get(_construct_url('getuserbalance'))

    for key in ['confirmed', 'unconfirmed']:
        balance += r_balance.json()['getuserbalance']['data'][key]

    return balance


def get_paid_from_txs():
    r_transacts = requests.get(_construct_url('getusertransactions'))
    summary = r_transacts.json()['getusertransactions']['data']['transactionsummary']

    # NOTE: paid + fees + txfee + balance == credit
    paid = summary['Debit_AP']
    # fees = summary['Fee']
    # txfee = summary['TXFee']
    # credit = summary['Credit']

    return paid


if __name__ == '__main__':
    total = get_balance() + get_paid_from_txs()
    print(total)
