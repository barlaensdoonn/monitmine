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

    def _average_sps(self):
        self.average_sps = int(self.sps / self.polls)

    def poll(self):
        self.stats = self._get_stats()
        self.polls += 1
        self._get_time_up()
        self._get_sps()
        self._average_sps()


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
                print('average_sps: {} over {} polls\n'.format(miner.average_sps, miner.polls))

    except KeyboardInterrupt:
        print('\nexiting...')
        polling = False
