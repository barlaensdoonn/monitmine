#!/usr/local/bin/python3
# mining monitor
# 6/22/17


import minor
import requests
from datetime import datetime


class Miner(object):
    'interact with the miner api'

    miner_url = minor.miner_url

    def __init__(self):
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

    def get_time_up(self):
        self.time_up = datetime.now() - self.start_time


if __name__ == '__main__':
    miner = Miner()
    polling = True

    while polling:
        if int(datetime.now().timestamp() % 5) == 0:
            print('exiting at {}'.format(datetime.now()))
            polling = False
