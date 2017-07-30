#!/usr/local/bin/python3
# claymore miner api monitor
# 7/03/17
# updated 7/30/17

import sys
import json
import minor
import socket
import logging
from datetime import datetime, timedelta


class Miner(object):
    '''interact with the Claymore miner api'''

    watts = {1: 300, 2: 600}  # rough watts pulled by system mining with 1 & 2 gpus
    request = {'method': 'miner_getstat1', 'jsonrpc': '2.0', 'id': 0}

    api_response_labels = [
        'version',
        'mins_up',
        ['hashrate_mhs', 'accepted_shares', 'rejected_shares'],
        'gpu_hashrate_mhs',
        ['hashrate_mhs_alt', 'accepted_shares_alt', 'rejected_shares_alt'],
        'gpu_hashrate_mhs_alt',
        ['gpu_temperature', 'gpu_fan_speed'],
        'current_pools',
        ['num_invalid_shares', 'num_pool_switches', 'num_invalid_shares_alt', 'num_pool_switches_alt']
    ]

    def __init__(self):
        self._initialize_logger()
        self.polls = 0
        self.request = json.dumps(self.request)
        self._update_stats()
        self.miner_version = self.stats['version']
        self.mins_up = int(self.stats['mins_up'])
        self.start_time = datetime.now() - timedelta(minutes=self.mins_up)
        self.up_time = 0
        self.gpus = self._get_number_of_gpus()
        self.pools = self.stats['current_pools']
        self.coins = [self.pools[i][0:3] for i in range(len(self.pools))]

        self.gpu_stats = {
            i: {
                'gpu_temperature': {'total': 0, 'average': 0},
                'gpu_fan_speed': {'total': 0, 'average': 0},
                'gpu_hashrate_mhs': {'total': 0, 'average': 0},
                'gpu_hashrate_mhs_alt': {'total': 0, 'average': 0}
            } for i in range(self.gpus)
        }

        self.session_stats = {
            # NOTE: other available stats: ['num_invalid_shares', num_invalid_shares_alt', 'num_pool_switches', 'num_pool_switches_alt']
            'gpu_temperature': {'total': 0, 'average': 0},
            'gpu_fan_speed': {'total': 0, 'average': 0},
            'hashrate_mhs': {'total': 0, 'average': 0},
            'hashrate_mhs_alt': {'total': 0, 'average': 0},
            'accepted_shares': {'total': 0, 'average': 0},
            'rejected_shares': {'total': 0, 'average': 0},
            'accepted_shares_alt': {'total': 0, 'average': 0},
            'rejected_shares_alt': {'total': 0, 'average': 0},
            'shares_per_min': {'total': 0, 'average': 0},
            'shares_per_min_alt': {'total': 0, 'average': 0},
            'kWhs': {'consumed': 0, 'cost': 0}
        }

    def _initialize_logger(self):
        self.logger = logging.getLogger('claymore')
        self.logger.info('* * * * * * * * * * * * * * * * * * * *')
        self.logger.info('claymore logger instantiated')
        self.logger.info('monitoring session started')

    def _get_number_of_gpus(self):
        if isinstance(self.stats['gpu_hashrate_mhs'], list):
            return len(self.stats['gpu_hashrate_mhs'])
        else:
            return 1

    def _get_up_time(self):
        self.up_time = datetime.now() - self.start_time

    def _create_client(self):
        host = minor.claymore_host
        port = minor.claymore_port

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

    def _convert_to_int(self, thing):
        try:
            thing = int(thing)
        except ValueError:
            pass

        return thing

    def _parse_stats(self):
        for i in range(len(self.stats)):
            if ';' in self.stats[i]:
                self.stats[i] = self.stats[i].split(';')
                for j in range(len(self.stats[i])):
                    self.stats[i][j] = self._convert_to_int(self.stats[i][j])
            else:
                self.stats[i] = self._convert_to_int(self.stats[i])

    def _zip_stats(self):
        zipped_stats = {}

        for stat in zip(self.api_response_labels, self.stats):
            if isinstance(stat[0], list):
                for i in range(len(stat[0])):
                    zipped_stats[stat[0][i]] = stat[1][i]
            else:
                zipped_stats[stat[0]] = stat[1]

        self.stats = zipped_stats

    def _get_stats(self):
        retries = 5

        while retries:
            try:
                self._create_client()
                self.client.send(self.request.encode('ascii'))
                response = self.client.recv(1024)

                stats = json.loads(response.decode('ascii'))

                if not stats['error']:
                    self.stats = stats['result']
                    return
                else:
                    self.logger.error('could not get stats due to error {}'.format(stats['error']))
                    retries -= 1

            except Exception as e:
                self.logger.error('could not connect to miner for the following reason:')
                self.logger.error(e)
                retries -= 1

        self.logger.error('connect retries exhausted, exiting...')
        sys.exit()

    def _update_stats(self):
        self._get_stats()
        self._parse_stats()
        self._zip_stats()


if __name__ == '__main__':
    miner = Miner()
    for key in miner.stats.keys():
        print('{}: {}'.format(key, miner.stats[key]))
