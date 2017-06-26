#!/usr/local/bin/python3
# mining monitor
# 6/24/17
# updated 6/26/17


import coin
import ewbf_miner
import earnings
import time
from datetime import datetime


if __name__ == '__main__':
    miner = ewbf_miner.Miner()
    zec = coin.Coin('zec')
    earnings = earnings.Earnings(zec, miner)

    polling = True

    try:
        while polling:
            if int(datetime.now().timestamp() % 30) == 0:
                miner.poll()
                earnings.update()
                time.sleep(1)

    except KeyboardInterrupt:
        print('\nexiting...')
        polling = False
