#!/usr/local/bin/python3
# check coin balances via nanopool api
# 6/22/17
# updated 7/28/17

import yaml
import dcrd_modular as dcrd
import nnpl
import minor
import logging
import logging.config


class Coin(object):
    '''basic functions to interact with nanopool api'''

    def __init__(self, key, interface):
        self.key = key
        self.currency = self.key[0:3]
        self.interface = interface
        self.balance = 0
        self.payments = {}
        self.paid = 0
        self.total = 0
        self.btc = 0
        self.usd = 0

        self.prices = {
            'btc': 0,
            'usd': 0
        }

    def _get_total(self):
        self.balance = self.interface.get_balance()
        self.paid = self.interface.get_paid()

        self.total = self.balance + self.paid

        if self.key == 'zec':
            self.total -= self.interface.get_lew()

    def _convert_to_prices(self):
        self.get_prices()

        self.btc = self.total * self.prices['btc']
        self.usd = self.total * self.prices['usd']

    def get_payments(self):
        self.payments = self.interface.get_payments()

    def get_last_payment(self):
        self.get_payments()

        return self.payments[0]

    def get_prices(self):
        prices = self.interface.get_prices()

        self.prices['btc'] = prices['price_btc']
        self.prices['usd'] = prices['price_usd']

    def update(self):
        self._get_total()
        self._convert_to_prices()

        self.info = {
            'balance': self.balance,
            'paid': self.paid,
            'total': self.total,
            'total_btc': self.btc,
            'total_usd': self.usd,
            'price': self.prices['usd']
        }


def initialize_logger():
    with open(minor.log_conf, 'r') as log_conf:
        log_config = yaml.safe_load(log_conf)

    logging.config.dictConfig(log_config)
    logger = logging.getLogger('coin')
    logger.info('* * * * * * * * * * * * * * * * * * * *')
    logger.info('coin logger instantiated')

    return logger


if __name__ == '__main__':
    logger = initialize_logger()
    stat_order = ['balance', 'paid', 'total', 'total_btc', 'total_usd', 'price']
    coins = [key for key in minor.addresses.keys()]
    total_usd = 0
    total_btc = 0

    for currency in coins:
        if currency == 'dcr':
            api = dcrd.Dcrd()
        else:
            api = nnpl.Nnpl(currency)

        altcoin = Coin(currency, api)
        altcoin.update()

        total_usd += altcoin.info['total_usd']
        total_btc += altcoin.info['total_btc']

        logger.info(' - - - {} - - - '.format(currency.upper()))

        for key in stat_order:
            logger.info('{}: {:.6f}'.format(key, altcoin.info[key]))

        logger.info(' - - - - - - - - ')

    logger.info(' - - - TOTAL - - - ')
    logger.info('total_usd: {:.6f}'.format(total_usd))
    logger.info('total_btc: {:.6f}'.format(total_btc))
    logger.info(' - - - - - - - - ')
