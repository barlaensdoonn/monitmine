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

    claymore_miner = claymore_miner.Miner()
    ewbf_miner = ewbf_miner.Miner()
    ewbf_coin = coin.Coin(ewbf_miner.coin)
    ewbf_earnings = earnings.Earnings(ewbf_coin, ewbf_miner)

    polling = True

    try:
        while polling:
            if int(datetime.now().timestamp() % 30) == 0:
                ewbf_miner.poll()
                ewbf_earnings.update()
                time.sleep(1)

    except KeyboardInterrupt:
        claymore_miner.logger.info('...user exit received...')
        ewbf_earnings.logger.info('...user exit received...')
        logging.info('...user exit received...')
        logging.info('exiting...')
        polling = False
