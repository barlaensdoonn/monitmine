#!/usr/local/bin/python3
# check coin balances
# 6/22/17


import minor
import requests


class Coin(object):
    'basic functions to interact with nanopool api'

    addresses = minor.addresses

    def __init__(self, coin):
        self.coin = coin
        self.address = self.addresses[coin]
        self.balance = 0
        self.paid = 0
        self.total = 0
        self.price_btc = 0
        self.price_usd = 0
        self.btc = 0
        self.usd = 0

    def _construct_url(self, action):
        if action == 'prices':
            return 'https://api.nanopool.org/v1/{coin}/{action}'.format(coin=self.coin, action=action)
        else:
            return 'https://api.nanopool.org/v1/{coin}/{action}/{acct}'.format(coin=self.coin, action=action, acct=self.address)

    def _request(self, action):
        url = self._construct_url(action)
        r = requests.get(url)

        if r.status_code == 200:
            jsn = r.json()
            return jsn['data']
        else:
            return None

    def _get_balance(self):
        amount = self._request('balance')

        if amount:
            self.balance = amount

    def _get_payments(self):
        payments = self._request('payments')

        if payments:
            for payment in payments:
                self.paid += payment['amount']

    def _get_total(self):
        self._get_balance()
        self._get_payments()
        self.total = self.balance + self.paid

    def _convert_to_prices(self):
        prices = self._request('prices')

        self.price_btc = prices['price_btc']
        self.price_usd = prices['price_usd']

        self.btc = self.total * self.price_btc
        self.usd = self.total * self.price_usd

    def update(self):
        self._get_total()
        self._convert_to_prices()

        self.info = {
            'balance': self.balance,
            'payments': self.paid,
            'total': self.total,
            'total_in_btc': self.btc,
            'total_in_usd': self.usd,
            'price': self.price_usd
        }


if __name__ == '__main__':
    stat_order = ['balance', 'payments', 'total', 'total_in_btc', 'total_in_usd', 'price']
    coins = ['eth', 'sia', 'zec']

    for currency in coins:
        altcoin = Coin(currency)
        altcoin.update()

        print(' - - - {} - - - '.format(currency.upper()))

        for key in stat_order:
            print('{}: {:.6f}'.format(key, altcoin.info[key]))

        print(' - - - - - - - - \n')
