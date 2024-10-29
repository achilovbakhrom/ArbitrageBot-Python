from celery import shared_task
import time

from process.CachedClient import CachedClient
from .config import chains, AMOUNT, THRESHOLD, REPEAT_TIMES, DEBUG
from .utils import to_pairs

@shared_task
def heavy_task():
    client = CachedClient()

    total: float = 0
    for _ in range(REPEAT_TIMES):
        for chain in chains:
            pairs = to_pairs(chain)
            begin_amount = AMOUNT
            result: float = 0
            for [idx, pair] in enumerate(pairs):
                time.sleep(0.3)
                price = client.get_last_price_of_symbol(symbol=pair)
                print(f'ticker: {pair} {price}')
                if idx == 0:
                    result = begin_amount / price
                else:
                    result *= price

            diff = result - begin_amount
            calc_threshold = diff / begin_amount
            print(f''
                  f'calculated_result: {result},'
                  f'diff: {diff},'
                  f'calc_threshold: {calc_threshold},'
                  f'threshold: {THRESHOLD},'
                  f'isTrade: {calc_threshold > THRESHOLD}'
                )

            if DEBUG:
                continue

            traded = False

            initial_amount = AMOUNT
            qty = AMOUNT
            trade_result = 0.0

            if calc_threshold > THRESHOLD: # ratio
                traded = True

                for [idx, symbol] in enumerate(pairs):
                    print(f'symbol: {symbol}')
                    if idx == 0:
                        order, err_msg = client.create_buy_order(symbol=symbol, amount=qty)
                    else:
                        order, err_msg = client.create_sell_order(symbol=symbol, amount=qty)

                    if order is None:
                        raise ValueError(err_msg)

                    order = client.check_order(order=order, symbol=symbol)

                    if order is None:
                        raise ValueError('Order check is failed')

                    qty = float(order['cummulativeQuoteQty'])

                    if idx == len(pairs) - 1:
                        trade_result = qty
                        print('traded successfully')

            if traded:
                diff = trade_result - initial_amount
                total += diff
                print('----------------******----------------\n\n')
                print(f'BEGIN_AMOUNT: {initial_amount}')
                print(f'PROFIT: {diff}')
                print(f'TOTAL IN CYCLE: {total}')
                print('----------------******----------------\n\n')


    return 'task completed'