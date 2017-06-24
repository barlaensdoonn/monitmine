#!/usr/local/bin/python3
# mining monitor
# 6/22/17

# temp, gpu_power_usage, speed_sps updated by api every 30 seconds

import sys
import time
import minor
import requests
from datetime import datetime


class Miner(object):
    'interact with the miner api'

    miner_url = minor.miner_url

    def __init__(self):
        self.polls = 0
        self.sps = 0
        self.average_sps = 0
        self.stats = self._get_stats()
        self.start_time = datetime.fromtimestamp(self._get_start_time())
        self.shares = {
            'total': {i: 0 for i in range(len(self.stats['result']))},
            'average': {i: 0 for i in range(len(self.stats['result']))}
        }

    def _get_stats(self):
        try:
            r = requests.get(self.miner_url)
            return r.json()
        except ConnectionError:
            print('could not connect to the miner')

    def _get_start_time(self):
        return self.stats['result'][0]['start_time']

    def _get_time_up(self):
        self.time_up = datetime.now() - self.start_time

    def _get_sps(self):
        for gpu in self.stats['result']:
            self.sps += gpu['speed_sps']

        self.average_sps = int(self.sps / self.polls)

    def _get_shares(self):
        'to properly average shares over time this calculation should be running when miner starts'

        for i in range(len(self.stats['result'])):
            self.shares['total'][i] = self.stats['result'][i]['accepted_shares']
            self.shares['average'][i] = int(self.shares['total'][i] / self.polls)

    def poll(self):
        self.stats = self._get_stats()
        self.polls += 1
        self._get_time_up()
        self._get_sps()
        self._get_shares()


if __name__ == '__main__':
    miner = Miner()
    polling = True

    try:
        while polling:
            if int(datetime.now().timestamp() % 30) == 0:
                miner.poll()
                time.sleep(1)

                print('time up: {}'.format(miner.time_up))
                print('total sps: {}'.format(miner.sps))
                print('average_sps: {} over {} polls'.format(miner.average_sps, miner.polls))

                for key in miner.shares:
                    for gpu in miner.shares[key]:
                        print('{} shares for gpu{}: {}'.format(key, gpu, miner.shares[key][gpu]))

                print('\n')

    except KeyboardInterrupt:
        print('\nexiting...')
        polling = False
