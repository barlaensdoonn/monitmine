#!/usr/local/bin/python3
# eth, sia, zec via nanopool api
# 7/29/17
# updated 11/7/17

import minor
import pickle
import requests
import logging
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
        retries = 5

        while retries:
            try:
                r = requests.get(self._construct_url(action))

                if r.json()['status'] is True:
                    return r.json()['data']
                else:
                    logging.debug("r.json()['status'] == False for action: {}, key: {}. probably an old account, returning 0")
                    return 0
            except KeyError:
                if retries > 1:
                    logging.error("KeyError calling r.json()['data'] for action: {}, key: {}. retrying request...".format(action, self.key.upper()))

                retries -= 1

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

    def get_hashrate(self):
        return self._request('hashrate')
