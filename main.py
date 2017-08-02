#!/usr/local/bin/python3
# mining monitor
# 6/24/17
# updated 7/30/17

import yaml
import time
import logging
import logging.config
from datetime import datetime
import coin
import nnpl
import minor
import earnings
import ewbf_miner
import claymore_miner


if __name__ == '__main__':
    with open(minor.log_conf, 'r') as log_conf:
        log_config = yaml.safe_load(log_conf)

    logging.config.dictConfig(log_config)

    # claymore_miner = claymore_miner.Miner()
    ewbf_main = ewbf_miner.Miner(minor.ewbf_main, minor.ewbf_main_name)
    ewbf_xtra = ewbf_miner.Miner(minor.ewbf_xtra, minor.ewbf_xtra_name)
    ewbf_coin = coin.Coin(ewbf_main.coin, nnpl.Nnpl(ewbf_main.coin))
    zec_earnings = earnings.Earnings(ewbf_coin, ewbf_main)

    polling = True

    try:
        while polling:
            if int(datetime.now().timestamp() % 30) == 0:
                ewbf_main.poll()
                ewbf_xtra.poll()
                zec_earnings.update()
                time.sleep(1)

    except KeyboardInterrupt:
        # claymore_miner.logger.info('...user exit received...')
        ewbf_main.logger.info('...user exit received...')
        zec_earnings.logger.info('...user exit received...')
        logging.info('...user exit received...')
        logging.info('exiting...')
