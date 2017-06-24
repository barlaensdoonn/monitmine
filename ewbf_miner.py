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

    def __init__(self):
        self.polls = 0
        self.stats = self._get_stats()
        self.start_time = datetime.fromtimestamp(self._get_start_time())
        self.shares = {
            'total': {i: 0 for i in range(len(self.stats['result']))},
            'average': {i: 0 for i in range(len(self.stats['result']))}
        }
        self.sps = {
            'total': {i: 0 for i in range(len(self.stats['result']))},
            'average': {i: 0 for i in range(len(self.stats['result']))},
            'session_total': 0,
            'session_average': 0
        }

    def _get_stats(self):
        retries = 5

        while retries:
            try:
                r = requests.get(self.miner_url)
                return r.json()
            except ConnectionError:
                print('could not connect to miner\n')
                retries -= 1

        print('connect retries exhausted, exiting...')
        sys.exit()

    def _get_start_time(self):
        return self.stats['result'][0]['start_time']

    def _get_time_up(self):
        self.time_up = datetime.now() - self.start_time

    def _get_sps(self):
        for i in range(len(self.stats['result'])):
            current_sps = self.stats['result'][i]['speed_sps']
            self.sps['total'][i] += current_sps
            self.sps['average'][i] = int(self.sps['total'][i] / self.polls)
            self.sps['session_total'] += current_sps

        self.sps['session_average'] = int(self.sps['session_total'] / self.polls)

    def _get_shares(self):
        for i in range(len(self.stats['result'])):
            self.shares['total'][i] = self.stats['result'][i]['accepted_shares']
            self.shares['average'][i] = int(self.shares['total'][i] / self.polls)

    def _print_stats(self):
        print('time up: {}'.format(self.time_up))

        for gpu in self.sps['average']:
            print('average sps for gpu{}: {}'.format(gpu, self.sps['average'][gpu]))

        print('session average sps: {} over {} polls'.format(self.sps['session_average'], self.polls))

        for gpu in miner.shares['total']:
            print('total shares for gpu{}: {}'.format(gpu, self.shares['total'][gpu]))

        print('\n')

    def poll(self):
        self.stats = self._get_stats()
        self.polls += 1
        self._get_time_up()
        self._get_sps()
        self._get_shares()
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
