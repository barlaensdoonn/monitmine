#!/usr/local/bin/python3
# decred via suprnova [MPOS] api
# 7/22/17
# updated 7/29/17

import bttrx
import minor
import requests
from datetime import datetime, timedelta


# NOTE: getusertransactions only returns last 100 transactions
actions = ['getuserstatus', 'getuserbalance', 'getdashboarddata', 'getusertransactions', 'getuserhashrate']
api_key = minor.suprnova_key


def _construct_url(action):
    return 'https://dcr.suprnova.cc/index.php?page=api&action={}&api_key={}'.format(action, api_key)


def _request(action):
    r = requests.get(_construct_url(action))

    return r.json()[action]['data']


def _convert_to_datetime(pymnt_lst):
    '''timestamps from suprnova seem to be 9 hours ahead'''

    for pymnt in pymnt_lst:
        pymnt['timestamp'] = datetime.strptime(pymnt['timestamp'], '%Y-%m-%d %H:%M:%S')
        pymnt['date'] = pymnt['timestamp'] - timedelta(hours=9)

        return pymnt_lst


def get_prices():
    btc_dcrd = bttrx.get_price('btc', 'dcr')
    usd_btc = bttrx.get_price('usdt', 'btc')
    usd_dcrd = btc_dcrd * usd_btc

    return {'price_btc': btc_dcrd, 'price_usd': usd_dcrd}


def get_balance():
    balance = 0
    r_balance = _request('getuserbalance')

    for key in ['confirmed', 'unconfirmed']:
        balance += r_balance[key]

    return balance


def get_paid():
    r_txs = _request('getusertransactions')
    summary = r_txs['transactionsummary']

    # NOTE: paid + fees + txfee + balance == credit
    paid = summary['Debit_AP']
    # fees = summary['Fee']
    # txfee = summary['TXFee']
    # credit = summary['Credit']

    return paid


def get_payments():
    # NOTE: all possible tx types: ['Bonus', 'Credit', 'Credit_PPS', 'Debit_AP', 'Debit_MP', 'Fee', 'TXFee']
    # NOTE: all keys in tx instance: ['amount', 'blockhash', 'coin_address', 'confirmations', 'height', 'id', 'timestamp', 'txid', 'type', 'username']
    # NOTE: string format for tx['date']: '%Y-%m-%d %H:%M:%S' (currently seems to be 9 hours ahead)

    pymnt_types = ['Bonus', 'Credit', 'Credit_PPS', 'Debit_AP', 'Debit_MP']
    pymnts = []

    r_txs = _request('getusertransactions')
    txs = r_txs['transactions']

    for i in range(len(txs)):
        if txs[i]['type'] in pymnt_types:
            tx = {key: txs[i][key] for key in ['amount', 'timestamp', 'id']}
            pymnts.append(tx)

    return _convert_to_datetime(pymnts)
