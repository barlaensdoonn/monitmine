#!/usr/local/bin/python3
# mining monitor
# 6/24/17
# updated 8/3/17

import yaml
import time
import requests
import logging
import logging.config
from datetime import datetime
import coin
import nnpl
import minor
import earnings
import ewbf_miner


def check_for_miners(maybe_dict):
    '''
    miners dict format:

    miners = {
        'name': {
            'url': '',
            'miner': Miner()
        }
    }
    '''
    miners = {}

    for name in maybe_dict:
        url = maybe_dict[name]['url']

        try:
            r = requests.get(url)
            if r.status_code == 200:
                miners[name] = maybe_dict[name]
                miners[name]['miner'] = ewbf_miner.Miner(url, name)
        except Exception:
            logging.info("couldn't connect to {}, probably not mining".format(name))
        except KeyboardInterrupt:
            logging.info('...user exit received...')

    return miners


def get_max(miner_dict):
    up_times = {name: miner_dict[name]['miner'].up_time for name in miner_dict}

    # found max solution here: https://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
    return max(up_times, key=lambda key: up_times[key])


if __name__ == '__main__':
    with open(minor.log_conf, 'r') as log_conf:
        log_config = yaml.safe_load(log_conf)

    logging.config.dictConfig(log_config)
    miners = check_for_miners(minor.maybe_miners)

    if miners:
        older = get_max(miners)
        older_coin = miners[older]['miner'].coin
        ewbf_coin = coin.Coin(older_coin, nnpl.Nnpl(older_coin))
        zec_earnings = earnings.Earnings(ewbf_coin, miners[older]['miner'])

        polling = True

        try:
            while polling:
                if int(datetime.now().timestamp() % 30) == 0:
                    for miner in miners:
                        miners[miner]['miner'].poll()
                    zec_earnings.update()
                    time.sleep(1)

        except KeyboardInterrupt:
            for miner in miners:
                miners[miner]['miner'].logger.info('...user exit received...')
            zec_earnings.logger.info('...user exit received...')
            logging.info('...user exit received...')
            polling = False

    else:
        logging.error('could not connect to any miners')
