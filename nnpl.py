#!/usr/local/bin/python3
# eth, sia, zec via nanopool api
# 7/29/17
# updated 8/17/17

import minor
import pickle
import requests
from datetime import datetime


class Nnpl(object):
    '''basic functions to interact with nanopool api'''

    addresses = minor.addresses

    def __init__(self, key):
        self.key = key
        self.currency = self.key[0:3]
        self.address = self.addresses[self.key]
        self.payments = {}

    def _construct_url(self, action):
        if action == 'prices':
            return 'https://api.nanopool.org/v1/{currency}/{action}'.format(currency=self.currency, action=action)
        else:
            return 'https://api.nanopool.org/v1/{currency}/{action}/{acct}'.format(currency=self.currency, action=action, acct=self.address)

    def _request(self, action):
        r = requests.get(self._construct_url(action))

        if r.status_code == 200:
            return r.json()['data']
        else:
            return None

    def _convert_to_datetime(self):
        for pymnt in self.payments:
            pymnt['date'] = datetime.fromtimestamp(pymnt['date'])

    def get_lew(self):
        lews_cut = 0.25
        balance = self.get_balance()
        lew_paid = lews_cut * balance

        with open(minor.lew_pymnts, 'rb') as pckl:
            lew = pickle.load(pckl)

        lew_paid += lew
        return lew_paid

    def get_balance(self):
        return self._request('balance')

    def get_payments(self):
        self.payments = self._request('payments')

        if self.payments:
            self._convert_to_datetime()

        return self.payments

    def get_paid(self):
        paid = 0
        self.get_payments()

        for payment in self.payments:
            paid += payment['amount']

        return paid

    def get_prices(self):
        return self._request('prices')
