#!/usr/local/bin/python3
# mining monitor
# 6/24/17
# updated 6/25/17


import coin
import ewbf_miner
import time
from datetime import datetime


def initialize_balances(coin, miner):
    miner.initial_balance = coin.get_balance()
    miner.last_payment = coin.get_last_payment()


if __name__ == '__main__':
    miner = ewbf_miner.Miner()
    zec = coin.Coin('zec')

    initialize_balances(zec, miner)
    polling = True

    try:
        while polling:
            if int(datetime.now().timestamp() % 30) == 0:
                miner.poll()
                time.sleep(1)

    except KeyboardInterrupt:
        print('\nexiting...')
        polling = False
