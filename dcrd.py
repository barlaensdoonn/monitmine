#!/usr/local/bin/python3
# decred via suprnova [MPOS] api
# 7/22/17
# updated 7/28/17

import minor
import requests

# NOTE: getusertransactions only returns last 100 transactions
actions = ['getuserstatus', 'getuserbalance', 'getdashboarddata', 'getusertransactions', 'getuserhashrate']
crrncys = ['btc', 'eth', 'zec', 'dcr', 'sia']
xchngs = ['usdt', 'btc']


def _construct_url(*args):
    if args[0] in actions:
        return 'https://dcr.suprnova.cc/index.php?page=api&action={}&api_key={}'.format(args[0], minor.suprnova_key)
    else:
        return 'https://bittrex.com/api/v1.1/public/getticker?market={}-{}'.format(args[0].upper(), args[1].upper())


def get_price(xchng, crrncy):
    if crrncy.lower() == 'sia':
        crrncy = 'sc'

    r = requests.get(_construct_url(xchng, crrncy))

    return r.json()['result']['Last']


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
