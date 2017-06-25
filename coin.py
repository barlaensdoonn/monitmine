#!/usr/local/bin/python3
# check coin balances via nanopool api
# 6/22/17
# updated 6/24/17


import minor
import requests


class Coin(object):
    'basic functions to interact with nanopool api'

    addresses = minor.addresses

    def __init__(self, coin):
        self.coin = coin
        self.address = self.addresses[coin]
        self.balance = 0
        self.payments = {}
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
            return r.json()['data']
        else:
            return None

    def _get_total(self):
        self.get_balance()
        self.get_payments()
        self.total = self.balance + self.paid

    def _convert_to_prices(self):
        prices = self._request('prices')

        self.price_btc = prices['price_btc']
        self.price_usd = prices['price_usd']

        self.btc = self.total * self.price_btc
        self.usd = self.total * self.price_usd

    def get_balance(self):
        amount = self._request('balance')

        if amount:
            self.balance = amount

        return self.balance

    def get_payments(self):
        self.payments = self._request('payments')

        if self.payments:
            for payment in self.payments:
                self.paid += payment['amount']

    def get_last_payment(self):
        self.get_payments()

        return self.payments[-1]

    def update(self):
        self._get_total()
        self._convert_to_prices()

        self.info = {
            'balance': self.balance,
            'paid': self.paid,
            'total': self.total,
            'total_btc': self.btc,
            'total_usd': self.usd,
            'price': self.price_usd
        }


if __name__ == '__main__':
    stat_order = ['balance', 'paid', 'total', 'total_btc', 'total_usd', 'price']
    coins = [key for key in minor.addresses.keys()]
    total_usd = 0
    total_btc = 0

    for currency in coins:
        altcoin = Coin(currency)
        altcoin.update()

        total_usd += altcoin.info['total_usd']
        total_btc += altcoin.info['total_btc']

        print(' - - - {} - - - '.format(currency.upper()))

        for key in stat_order:
            print('{}: {:.6f}'.format(key, altcoin.info[key]))

        print(' - - - - - - - - \n')

    print(' - - - TOTAL - - - ')
    print('total_usd: {:.6f}'.format(total_usd))
    print('total_btc: {:.6f}'.format(total_btc))
    print(' - - - - - - - - \n')
