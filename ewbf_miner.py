#!/usr/local/bin/python3
# ewbf zec miner api monitor
# 6/22/17
# updated 6/29/17


# NOTE: temp, gpu_power_usage, speed_sps updated by api every 30 seconds
# NOTE: to properly average values this script should be launched right after miner starts and preferably right after % 30 seconds == 0

import sys
import minor
import requests
from datetime import datetime


class Miner(object):
    '''interact with the EWBF miner api'''

    miner_url = minor.miner_url
    cumulative = ['temperature', 'speed_sps']  # leaving out 'gpu_power_usage' since it's pretty much static
    not_cumulative = ['accepted_shares', 'rejected_shares']
    watts = {1: 300, 2: 600}  # rough watts pulled by system mining with 1 & 2 gpus

    def __init__(self):
        self.polls = 0
        self.stats = self._get_stats()
        self.start_time = datetime.fromtimestamp(self.stats['result'][0]['start_time'])
        self.up_time = 0
        self.gpus = len(self.stats['result'])

        self.gpu_stats = {
            i: {
                'busid': self.stats['result'][i]['busid'],
                'cudaid': self.stats['result'][i]['cudaid'],
                'gpuid': self.stats['result'][i]['gpuid'],
                'gpu_status': self.stats['result'][i]['gpu_status'],
                'name': self.stats['result'][i]['name'],
                'start_time': self.start_time,
                'solver': self.stats['result'][i]['solver'],
                'gpu_power_usage': {'total': 0, 'average': 0},
                'temperature': {'total': 0, 'average': 0},
                'speed_sps': {'total': 0, 'average': 0},
                'accepted_shares': {'total': 0, 'average': 0},
                'rejected_shares': {'total': 0, 'average': 0},
                'shares_per_min': 0
            } for i in range(self.gpus)
        }

        self.session_stats = {
            # 'gpu_power_usage': {'total': 0, 'average': 0},  # leaving out since it's pretty much static
            'temperature': {'total': 0, 'average': 0},
            'speed_sps': {'total': 0, 'average': 0},
            'accepted_shares': {'total': 0, 'average': 0},
            'rejected_shares': {'total': 0, 'average': 0},
            'kWhs': {'consumed': 0, 'cost': 0}
        }

    def _get_stats(self):
        retries = 5

        while retries:
            try:
                r = requests.get(self.miner_url)
                return r.json()
            except Exception as e:
                print('\ncould not connect to miner for the following reason:\n')
                print(e)
                retries -= 1

        print('connect retries exhausted, exiting...')
        sys.exit()

    def _get_up_time(self):
        self.up_time = datetime.now() - self.gpu_stats[0]['start_time']

    def _get_shares_per_min(self, gpu):
            up_time_mins = self.up_time.total_seconds() / 60
            self.gpu_stats[gpu]['shares_per_min'] = self.gpu_stats[gpu]['accepted_shares']['total'] / up_time_mins

    def _get_kwhs_consumed(self):
        self.session_stats['kWhs']['consumed'] = (self.watts[self.gpus] / 1000) * (self.up_time.total_seconds() / 60 / 60)
        self.session_stats['kWhs']['cost'] = self.session_stats['kWhs']['consumed'] * 0.13

    def _update_stats(self):
        self.stats = self._get_stats()

        for gpu in range(self.gpus):
            self._update_gpu_stats(gpu)
            self._get_shares_per_min(gpu)

        self._update_session_stats()
        self._get_kwhs_consumed()

    def _update_gpu_stats(self, gpu):
        for stat in self.cumulative:
            current_stat = self.stats['result'][gpu][stat]
            self.gpu_stats[gpu][stat]['total'] += current_stat
            self.gpu_stats[gpu][stat]['average'] = self.gpu_stats[gpu][stat]['total'] / self.polls

        for stat in self.not_cumulative:
            current_stat = self.stats['result'][gpu][stat]
            self.gpu_stats[gpu][stat]['total'] = current_stat
            self.gpu_stats[gpu][stat]['average'] = self.gpu_stats[gpu][stat]['total'] / self.polls

    def _update_session_stats(self):
        # might work?
        for gpu in range(self.gpus):
            for stat in self.cumulative:
                current_stat = self.stats['result'][gpu][stat]
                self.session_stats[stat]['total'] += current_stat

        for stat in self.not_cumulative:
            self.session_stats[stat]['total'] = 0
            for gpu in range(self.gpus):
                current_stat = self.stats['result'][gpu][stat]
                self.session_stats[stat]['total'] += current_stat

        for stat in self.session_stats:
            if stat in self.cumulative or stat in self.not_cumulative:
                self.session_stats[stat]['average'] = self.session_stats[stat]['total'] / self.polls

    def _print_stats(self):
        print('- - - - - - - - - - - - - - - - - -')
        print('start time: {}'.format(self.start_time))
        print('time up: {}'.format(self.up_time))

        print()

        for stat in self.cumulative:
            for gpu in self.gpu_stats:
                print('average {} gpu{}: {}'.format(stat, gpu, self.gpu_stats[gpu][stat]['average']))

        for stat in self.not_cumulative:
            for gpu in self.gpu_stats:
                print('total {} gpu{}: {}'.format(stat, gpu, self.gpu_stats[gpu][stat]['total']))

        print()

        for gpu in self.gpu_stats:
            print('shares per min gpu{}: {}'.format(gpu, self.gpu_stats[gpu]['shares_per_min']))

        print()

        for stat in self.session_stats:
            if stat in self.cumulative:
                print('session average {}: {}'.format(stat, self.session_stats[stat]['average']))
            elif stat in self.not_cumulative:
                print('session total {}: {}'.format(stat, self.session_stats[stat]['total']))
            else:
                for nested_stat in self.session_stats[stat]:
                    print('session {} {}: {}'.format(stat, nested_stat, self.session_stats[stat][nested_stat]))

        print('- - - - - - - - - - - - - - - - - -\n')

    def poll(self):
        self.polls += 1
        self._get_up_time()
        self._update_stats()
        self._print_stats()
