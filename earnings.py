#!/usr/local/bin/python3
# mining earnings monitor
# 6/24/17
# updated 8/17/17

import logging
from datetime import datetime


class Earnings(object):
    '''
    calculate miner earning statistics
    '''

    log_order = ['per_min', 'per_hour', 'per_day', 'per_month', 'per_year', 'session_total']

    def __init__(self, coin, miner):
        self._initialize_logger()
        self.coin = coin
        self.currency = coin.currency
        self.miner = miner
        self.late_launch = False
        self.recalculate = False

        self.balances = {
            'initial': 0,
            'most_recent': 0,
            'current': 0
        }

        self.payments = {
            'last': {},
            'most_recent': {},
            'this_session': []
        }

        self.rates = {
            'per_min': 0.01666666666667,
            'per_hour': 60,
            'per_day': 24,
            'per_month': 30.41666666666667,
            'per_year': 365
        }

        self.earnings = {
            'coin': {
                'session_total': 0,
                'per_min': 0,
                'per_hour': 0,
                'per_day': 0,
                'per_month': 0,
                'per_year': 0
            },
            'usd': {
                'session_total': 0,
                'per_min': 0,
                'per_hour': 0,
                'per_day': 0,
                'per_month': 0,
                'per_year': 0
            }
        }

        self._initialize()

    def _initialize_logger(self):
        self.logger = logging.getLogger('earnings')
        self.logger.info('* * * * * * * * * * * * * * * * * * * *')
        self.logger.info('earnings logger instantiated')
        self.logger.info('monitoring session started')

    def _check_past_payments(self):
        all_payments = self.coin.get_payments()

        for payment in all_payments:
            pay_date = payment['date']

            if pay_date > self.miner.start_time:
                self.payments['this_session'].append(payment)
                self.late_launch = True

    def _initialize(self):
        self._check_past_payments()
        self.payments['last'] = self.coin.get_last_payment()
        self._update_payments()
        self._update_balance()

        if not self.late_launch:
            self.balances['initial'] = self.balances['current']

    def _update_balance(self):
        balance_check = self.coin.get_balance()

        if balance_check is not None:
            self.balances['most_recent'] = balance_check

            if self.balances['most_recent'] != self.balances['current']:
                self.recalculate = True
                self.balances['current'] = self.balances['most_recent']

    def _update_payments(self):
        payment_check = self.coin.get_last_payment()

        if payment_check is not None:
            self.payments['most_recent'] = payment_check

            if self.payments['most_recent']['date'] != self.payments['last']['date']:
                self.recalculate = True
                self.payments['this_session'].insert(0, self.payments['most_recent'])
                self.payments['last'] = self.payments['most_recent']

    def _calculate_rates(self):
        self.earnings['coin']['per_min'] = self.earnings['coin']['session_total'] / self.miner.up_time.total_seconds() * 60
        self.earnings['coin']['per_hour'] = self.earnings['coin']['per_min'] * 60
        self.earnings['coin']['per_day'] = self.earnings['coin']['per_hour'] * 24
        self.earnings['coin']['per_year'] = self.earnings['coin']['per_day'] * 365
        self.earnings['coin']['per_month'] = self.earnings['coin']['per_year'] / 12

    def _convert_to_usd(self):
        self.coin.get_prices()

        for key in self.earnings['coin']:
            self.earnings['usd'][key] = self.earnings['coin'][key] * self.coin.prices['usd']

    def _recalculate_earnings(self):
        self.earnings['coin']['session_total'] = self.balances['current']

        if self.payments['this_session']:
            for payment in self.payments['this_session']:
                self.earnings['coin']['session_total'] += payment['amount']

        if not self.late_launch:
            self.earnings['coin']['session_total'] -= self.balances['initial']

        self._calculate_rates()
        self._convert_to_usd()
        self._log_earnings()

        self.recalculate = False

    def _log_earnings(self):
        self.logger.info('')
        self.logger.info('{} earnings updated at {}'.format(self.currency.upper(), datetime.now()))

        for key in self.earnings:
            self.logger.info('- - - - - - - - {} - - - - - - - - - '.format(key))
            for thing in self.log_order:
                self.logger.info('{}: {}'.format(thing, self.earnings[key][thing]))

    def update(self):
        self._update_balance()
        self._update_payments()

        if self.recalculate:
            self._recalculate_earnings()
