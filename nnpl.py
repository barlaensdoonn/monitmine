#!/usr/local/bin/python3
# eth, sia, zec via nanopool api
# 7/29/17
# updated 7/29/17

import minor
import pickle
import requests


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
        url = self._construct_url(action)
        r = requests.get(url)

        if r.status_code == 200:
            return r.json()['data']
        else:
            return None

    def get_lew(self):
        with open(minor.lew_pymnts, 'rb') as pckl:
            pymnts = pickle.load(pckl)

        return pymnts

    def get_balance(self):
        return self._request('balance')

    def get_payments(self):
        self.payments = self._request('payments')

        return self.payments

    def get_paid(self):
        paid = 0
        self.get_payments()

        for payment in self.payments:
            paid += payment['amount']

        return paid

    def get_prices(self):
        return self._request('prices')
