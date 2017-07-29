#!/usr/local/bin/python3
# bittrex api
# 7/22/17
# updated 7/28/17

import requests

xchngs = ['usdt', 'btc']
crrncys = ['btc', 'eth', 'zec', 'dcr', 'sia']


def _construct_url(*args):
    return 'https://bittrex.com/api/v1.1/public/getticker?market={}-{}'.format(args[0].upper(), args[1].upper())


def get_price(xchng, crrncy):
    # if crrncy.lower() == 'sia':
    #     crrncy = 'sc'

    r = requests.get(_construct_url(xchng, crrncy))

    return r.json()['result']['Last']
