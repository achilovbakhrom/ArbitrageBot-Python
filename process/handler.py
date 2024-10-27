from enum import Enum

from celery import shared_task
import time
from binance.client import Client
from django.db.models.expressions import result

SPLITTER = '-'
AMOUNT = 1000 # means $1000
USER_THRESHOLD = 0.0003 # means if THRESHOLD gt $0.5 0.1$
BINANCE_SLIPPAGE = 0.001

THRESHOLD = USER_THRESHOLD + BINANCE_SLIPPAGE

# 0.001%

class Coin(Enum):
    USDT = 'USDT'
    XRP = 'XRP'
    XLM = 'XLM'
    ETH = 'ETH'
    BTC = 'BTC'
    BNB = 'BNB'
    ADA = 'ADA'
    AVAX = 'AVAX'
    SOL = 'SOL'
    ATOM = 'ATOM'
    DOT = 'DOT'
    DYDX = 'DYDX'
    EGLD = 'EGLD'
    LDO = 'LDO'
    DOGE = 'DOGE'
    SHIB = 'SHIB'
    PEPE = 'PEPE'

    def __str__(self) -> str:
        return self.value


BASE_COIN = Coin.USDT

chains = [
    f'{Coin.USDT}-{Coin.AVAX}-{Coin.BTC}-{Coin.USDT}', # usdt - avax - btc - usdt
    f'{Coin.USDT}-{Coin.SOL}-{Coin.BTC}-{Coin.USDT}', # usdt - sol - btc - usdt
    f'{Coin.USDT}-{Coin.XLM}-{Coin.BTC}-{Coin.USDT}', # usdt - xlm - btc - usdt
    f'{Coin.USDT}-{Coin.XRP}-{Coin.BTC}-{Coin.USDT}', # usdt - xrp - btc - usdt
]

#AWS

def to_pairs(arg: str) -> [str]:
    if SPLITTER not in arg:
        raise ValueError(f'{arg} does not contain {SPLITTER}')

    splitted = arg.split(SPLITTER)

    length = len(splitted)

    if length <= 2:
        raise ValueError(f'{arg} should contain more than 2 coins')

    result: [str] = []
    for [index, coin] in enumerate(splitted):
        if index < length - 1:
            next_coin = splitted[index + 1]
            if coin == BASE_COIN.value:
                result.append(f'{next_coin}{coin}')
            else:
                result.append(f'{coin}{next_coin}')

    return result


@shared_task
def heavy_task():
    client = Client()
    total: float = 0
    for _ in range(100):
        for chain in chains:
            pairs = to_pairs(chain)
            begin_amount = AMOUNT
            result: float = 0
            for [idx, pair] in enumerate(pairs):
                time.sleep(0.3)
                ticker = client.get_ticker(symbol=pair)
                price = float(ticker["lastPrice"])
                print(f'ticker: {pair} {price}')
                if idx == 0:
                    result = begin_amount / price
                else:
                    result *= price

            diff = result - begin_amount
            print(f'result: {result}')
            print(f'diff: {diff / begin_amount} {THRESHOLD}')
            traded = False

            result = 0

            if diff / begin_amount > THRESHOLD: # ratio
                # trading part
                traded = True
                for [idx, pair] in enumerate(pairs):
                    ticker = client.get_ticker(symbol=pair) # usdt - avax - btc - usdt
                    price = float(ticker["lastPrice"])
                    print(f'ticker: {pair} {price}')
                    if idx == 0:
                        result = begin_amount / price
                    else:
                        result *= price
                    time.sleep(2)


            if traded:
                diff = result - begin_amount
                total += diff
                print('----------------******----------------\n\n')
                print(f'BEGIN_AMOUNT: {begin_amount}')
                print(f'PROFIT: {result - begin_amount}')
                print(f'TOTAL IN CYCLE: {total}')
                print('----------------******----------------\n\n')




    return 'task completed'

# 1. profit for pair
# 2. if condition allows - trade 1000 * 0

# 1. real trade try
# 2. BTC - XLM - 1000$ волатильность