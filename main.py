#!/usr/local/bin/python3
# mining monitor
# 6/24/17
# updated 7/09/17

import yaml
import time
import logging
import logging.config
from datetime import datetime
import coin
import minor
import earnings
import ewbf_miner
import claymore_miner


if __name__ == '__main__':
    with open(minor.log_conf, 'r') as log_conf:
        log_config = yaml.safe_load(log_conf)

    logging.config.dictConfig(log_config)

    claymore = claymore_miner.Miner()
    ewbf = ewbf_miner.Miner()
    zec = coin.Coin('zec')
    earnings = earnings.Earnings(zec, ewbf)

    polling = True

    try:
        while polling:
            if int(datetime.now().timestamp() % 30) == 0:
                ewbf.poll()
                earnings.update()
                time.sleep(1)

    except KeyboardInterrupt:
        print('\nexiting...')
        polling = False
