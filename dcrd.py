#!/usr/local/bin/python3
# decred via suprnova [MPOS] api
# 7/22/17
# updated 7/28/17

import bttrx
import minor
import requests


class Dcrd(object):
    '''basic functions to interact with suprnova [MPOS] api'''

    # NOTE: getusertransactions only returns last 100 transactions
    actions = ['getuserstatus', 'getuserbalance', 'getdashboarddata', 'getusertransactions', 'getuserhashrate']

    def __init__(self):
        self.api_key = minor.suprnova_key

    def _construct_url(self, action):
        return 'https://dcr.suprnova.cc/index.php?page=api&action={}&api_key={}'.format(action, self.api_key)

    def _request(self, action):
        return requests.get(self._construct_url(action))

    def get_prices(self):
        btc_dcrd = bttrx.get_price('btc', 'dcr')
        usd_btc = bttrx.get_price('usdt', 'btc')
        usd_dcrd = btc_dcrd * usd_btc

        return {'price_btc': btc_dcrd, 'price_usd': usd_dcrd}

    def get_balance(self):
        balance = 0
        r_balance = self._request('getuserbalance')

        for key in ['confirmed', 'unconfirmed']:
            balance += r_balance.json()['getuserbalance']['data'][key]

        return balance

    def get_paid(self):
        r_transacts = self._request('getusertransactions')
        summary = r_transacts.json()['getusertransactions']['data']['transactionsummary']

        # NOTE: paid + fees + txfee + balance == credit
        paid = summary['Debit_AP']
        # fees = summary['Fee']
        # txfee = summary['TXFee']
        # credit = summary['Credit']

        return paid
