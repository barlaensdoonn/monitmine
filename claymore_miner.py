#!/usr/local/bin/python3
# claymore miner api monitor
# 7/03/17
# updated 7/04/17

import json
import socket
import minor
from datetime import datetime, timedelta


class Miner(object):
    '''interact with the Claymore miner api'''

    watts = {1: 300, 2: 600}  # rough watts pulled by system mining with 1 & 2 gpus

    def __init__(self):
        self.polls = 0
        self.stats = self._get_stats()
        self.miner_version = self.stats[0]
        self.start_time = datetime.now() - timedelta(minutes=int(self.stats[1]))
        self.up_time = 0
        self.gpus = self._get_number_of_gpus()

        self.stats_lookup_table = {
            0: 'version',
            1: 'mins_up',
            2: ['total_mhs', 'total_shares', 'total_shares_rejected'],
            3: 'mhs_per_gpu',
            4: ['total_mhs_alt', 'total_shares_alt', 'total_shares_rejected_alt'],
            5: 'mhs_per_gpu_alt',
            6: ['temp', 'fan_speed'],
            7: 'current_pools',
            8: ['num_invalid_shares', 'num_pool_switches', 'num_invalid_shares_alt', 'num_pool_switches_alt']
        }

        self.gpu_stats = {
            i: {
                'temperature': {'total': 0, 'average': 0},
                'fan_speed': {'total': 0, 'average': 0},
                'hashrate_mhs': {'total': 0, 'average': 0},
                'hashrate_mhs_alt': {'total': 0, 'average': 0}
            } for i in range(self.gpus)
        }

        self.session_stats = {
            'temperature': {'total': 0, 'average': 0},
            'hashrate_mhs': {'total': 0, 'average': 0},
            'hashrate_mhs_alt': {'total': 0, 'average': 0},
            'accepted_shares': {'total': 0, 'average': 0},
            'rejected_shares': {'total': 0, 'average': 0},
            'accepted_shares_alt': {'total': 0, 'average': 0},
            'rejected_shares_alt': {'total': 0, 'average': 0},
            'kWhs': {'consumed': 0, 'cost': 0}
        }

    def _get_number_of_gpus(self):
        if ';' in self.stats[3]:
            return len(self.stats[2].split(';'))
        else:
            return 1

    def _get_up_time(self):
        self.up_time = datetime.now() - self.start_time

    def _create_client(self):
        host = minor.claymore_host
        port = minor.claymore_port

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

    def _create_request(self):
        request = {'method': 'miner_getstat1', 'jsonrpc': '2.0', 'id': 0}
        self.request = json.dumps(request)

    def _get_stats(self):
        self.client.send(self.request.encode('ascii'))
        response = self.client.recv(1024)

        stats = json.loads(response.decode('ascii'))

        if not stats['error']:
            return stats['result']
        else:
            print('could not get stats due to error {}'.format(stats['error']))
            return None
