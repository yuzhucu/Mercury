#coding: utf-8
import os
import time
import datetime
import bcolz
import pickle
import numpy as np
import pandas as pd

from instruments import Instrument

class DataProxy(object):
    """Read bcolz data and return data bar"""
    def __init__(self, root_dir):
        self.root_dir = root_dir
        bcolz.defaults.out_flavor = "numpy"
        self._futures_bar = bcolz.open(os.path.join(root_dir, 'futures.bcolz'))
        self._instruments = {k: Instrument(v)
                             for k,v in pickle.load(open(os.path.join(root_dir, 'instruments.pk'), 'rb')).items()}
        self._instruments_pos = self._futures_bar.attrs['line_map']
    
    def get_trading_bar(self, symbol, start_date, end_date):
        try:
            l, r = self._instruments_pos[symbol]
            symbol_bar = self._futures_bar[l:r]
            columns = ['date','symbol','open','exchange','lastprice','high','low','volume',
                       'bid','ask','uppderlimit','lowderlimit','bidvolume',
                       'askvolume','amt','chg','pct_chg','oi','close']
            ret_bar = symbol_bar[columns]
            df = pd.DataFrame(ret_bar, columns=columns)

            df['date'] = pd.DatetimeIndex([x.decode('utf-8') for x in df['date'].values])
            df['exchange'] = pd.Series([x.decode('utf-8') for x in df['exchange'].values])
            df['symbol'] = pd.Series([x.decode('utf-8') for x in df['symbol'].values])
            
            s = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            e = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            ret = df[df.date>=s]
            bar = ret[ret.date<=e]

            #Data bar is dataframe format with natural index
            return bar
        except KeyError as e:
            print('May be not find symbol:%s' % symbol)
        
"""Test Code"""
def main():
    dp = DataProxy('/Users/ruyiqf/mercury/Mercury/vob/data/')
    dp.get_trading_bar('IF1703', '2017-03-01', '2017-03-07')

if __name__ == '__main__':
    main()
