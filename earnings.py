#!/usr/local/bin/python3
# mining monitor
# 6/24/17
# updated 6/25/17


from datetime import datetime


class Earnings(object):
    '''calculate miner earning statistics'''

    def __init__(self, coin, miner):
        self.coin = coin
        self.currency = coin.coin
        self.miner = miner
        self.past_paid = False
        self.recalculate = False

        self.balances = {
            'initial': 0,
            'most_recent': 0,
            'current': 0
        }

        self.payments = {
            'initial': {},
            'last': {},
            'most_recent': {},
            'this_session': []
        }

        self.earnings = {
            'coin': {
                'session_total': 0,
                'per_minute': 0,
                'per_hour': 0,
                'per_day': 0,
                'per_month': 0
            },
            'usd': {
                'session_total': 0,
                'per_minute': 0,
                'per_hour': 0,
                'per_day': 0,
                'per_month': 0
            }
        }

    def _check_past_payments(self):
        all_payments = self.coin.get_payments()

        for payment in all_payments:
            pay_date = datetime.fromtimestamp(payment['date'])

            if pay_date > self.miner.start_time:
                payment.append(self.payments['this_session'])
                self.past_paid = True

    def initialize(self):
        past_paid = self._check_past_payments()

        if past_paid:
            self.payments['last'] = self.coin.get_last_payment()
        else:
            for key in ['initial', 'last']:
                self.payments[key] = self.coin.get_last_payment()

            self.balances['initial'] = self.payments['initial']['amount']

    def _update_balance(self):
        self.balances['most_recent'] = self.coin.get_balance()

        if self.balances['most_recent'] != self.balances['current']:
            self.recalculate = True
            self.balances['current'] = self.balances['most_recent']

    def _update_payments(self):
        self.payments['most_recent'] = self.coin.get_last_payment()

        if self.payments['most_recent']['txHash'] != self.payments['last']['txHash']:
            self.recalculate = True
            self.payments['this_session'].insert(0, self.payments['most_recent'])
            self.payments['last'] = self.payments['most_recent']

    def recalculate_earnings(self):
        self.earnings['session_total'] = self.balances['current']

        if self.payments['this_session']:
            for payment in self.payments['this_session']:
                self.earnings['session_total'] += payment['amount']

            if self.payments['initial']:
                self.earnings -= self.balances['initial']

        self.recalculate = False

    def update(self):
        self._update_balance()
        self._update_payments()

        if self.recalculate:
            self.recalculate_earnings()
