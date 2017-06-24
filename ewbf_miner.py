#!/usr/local/bin/python3
# mining monitor
# 6/22/17

# temp, gpu_power_usage, speed_sps updated by api every 30 seconds
# to properly average values this script should be running when miner starts

import sys
import time
import minor
import requests
from datetime import datetime


class Miner(object):
    '''interact with the miner api'''

    miner_url = minor.miner_url
    cumulative = ['gpu_power_usage', 'temperature', 'speed_sps']
    not_cumulative = ['accepted_shares', 'rejected_shares']

    def __init__(self):
        self.polls = 0
        self.stats = self._get_stats()
        self.gpus = len(self.stats['result'])

        self.gpu_stats = {
            i: {
                'busid': self.stats['result'][i]['busid'],
                'cudaid': self.stats['result'][i]['cudaid'],
                'gpuid': self.stats['result'][i]['gpuid'],
                'gpu_status': self.stats['result'][i]['gpu_status'],
                'name': self.stats['result'][i]['name'],
                'start_time': datetime.fromtimestamp(self.stats['result'][i]['start_time']),
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
            'gpu_power_usage': {'total': 0, 'average': 0},
            'temperature': {'total': 0, 'average': 0},
            'speed_sps': {'total': 0, 'average': 0},
            'accepted_shares': {'total': 0, 'average': 0},
            'rejected_shares': {'total': 0, 'average': 0}
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

    def _update_stats(self):
        self.stats = self._get_stats()

        for stat in self.cumulative:
            for i in range(self.gpus):
                current_stat = self.stats['result'][i][stat]
                self.gpu_stats[i][stat]['total'] += current_stat
                self.gpu_stats[i][stat]['average'] = self.gpu_stats[i][stat]['total'] / self.polls
                self.session_stats[stat]['total'] += current_stat
            self.session_stats[stat]['average'] = self.session_stats[stat]['total'] / self.polls

        for stat in self.not_cumulative:
            for i in range(self.gpus):
                current_stat = self.stats['result'][i][stat]
                self.gpu_stats[i][stat]['total'] = current_stat
                self.gpu_stats[i][stat]['average'] = self.gpu_stats[i][stat]['total'] / self.polls
                self.session_stats[stat]['total'] = current_stat
            self.session_stats[stat]['average'] = self.session_stats[stat]['total'] / self.polls

    def _print_stats(self):
        print('- - - - - - - - - - - - - - - - - - - - - - -')
        print('time up: {}'.format(self.up_time))

        print('\n')

        for stat in self.cumulative:
            for gpu in self.gpu_stats:
                print('average {} for gpu{}: {}'.format(stat, gpu, self.gpu_stats[gpu][stat]['average']))

        print('\n')

        for stat in self.not_cumulative:
            for gpu in self.gpu_stats:
                print('total {} for gpu{}: {}'.format(stat, gpu, self.gpu_stats[gpu][stat]['total']))

        print('\n')

        for stat in self.session_stats:
            if stat in self.cumulative:
                print('session average {}: {}'.format(stat, self.session_stats[stat]['average']))
            elif stat in self.not_cumulative:
                print('session total {}: {}'.format(stat, self.session_stats[stat]['total']))

        print('- - - - - - - - - - - - - - - - - - - - - - -\n')

    def poll(self):
        self.polls += 1
        self._get_up_time()
        self._update_stats()
        self._print_stats()


if __name__ == '__main__':
    miner = Miner()
    polling = True

    try:
        while polling:
            if int(datetime.now().timestamp() % 30) == 0:
                miner.poll()
                time.sleep(1)

    except KeyboardInterrupt:
        print('\nexiting...')
        polling = False
