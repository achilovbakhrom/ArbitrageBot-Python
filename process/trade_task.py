# from decimal import Decimal
#
# from celery import shared_task
#
# from process.CachedClient import CachedClient
# from .config import chains, AMOUNT, THRESHOLD, REPEAT_TIMES, DEBUG
# from .utils import to_pairs
#
# # FEE = 0.1 # % BINANCE FEE
#
# def number_to_decimal(arg: float):
#     return Decimal(str(arg))
#
# @shared_task
# def heavy_task():
#     client = CachedClient()
#
#     # buy_order = client.create_buy_order(symbol='BTCUSDT', amount=200)
#     # print(f'buy_order: {buy_order}')
#     # sell_order = client.create_sell_order(symbol='DOGEBTC', amount=291.0)
#     # print(f'sell_order: {sell_order}')
#     #
#     #
#     #
#     # return ''
#
#     total: float = 0
#     for _ in range(REPEAT_TIMES):
#         for chain in chains:
#             pairs = to_pairs(chain)
#             begin_amount = Decimal(AMOUNT)
#             result = Decimal('0')
#
#             coeff =  (number_to_decimal(100) - number_to_decimal(FEE)) / number_to_decimal(100) # 0.999
#
#             for [idx, pair] in enumerate(pairs):
#                 price = number_to_decimal(client.get_last_price_of_symbol(symbol=pair))
#                 print(f'ticker: {pair} {price} {result}')
#
#                 if idx == 0:
#                     result = begin_amount / price
#                 else:
#                     result *= price
#
#                 result *= coeff
#             # 50.5
#             diff = result - begin_amount
#             # (0.5 / 50)
#             calc_threshold = (diff / begin_amount) * number_to_decimal(100)
#
#             print(f''
#                   f'calculated_result: {result} USDT,'
#                   f'diff: {diff} USDT,'
#                   f'calc_threshold: {calc_threshold}%,'
#                   f'threshold: {THRESHOLD}%,'
#                   f'isTrade: {calc_threshold > number_to_decimal(THRESHOLD)}'
#                 )
#
#             if DEBUG:
#                 continue
#
#             traded = False
#
#             initial_amount = AMOUNT
#             qty = AMOUNT
#             trade_result = 0.0
#
#             if calc_threshold > number_to_decimal(THRESHOLD): # ratio
#                 traded = True
#
#                 for [idx, symbol] in enumerate(pairs):
#                     print(f'symbol: {symbol}')
#                     is_buy = idx == 0
#                     if is_buy:
#                         order, err_msg = client.create_buy_order(symbol=symbol, amount=qty)
#                     else:
#                         order, err_msg = client.create_sell_order(symbol=symbol, amount=qty)
#
#                     if order is None:
#                         raise ValueError(err_msg)
#
#                     order = client.check_order(order=order, symbol=symbol)
#
#                     if order is None:
#                         raise ValueError('Order check is failed')
#                     if is_buy:
#                         qty = float(order['executedQty'])
#                     else:
#                         qty = float(order['cummulativeQuoteQty'])
#
#                     if idx == len(pairs) - 1:
#                         trade_result = qty
#                         print('traded successfully')
#
#             if traded:
#                 diff = trade_result - initial_amount
#                 total += diff
#                 print('----------------******----------------\n\n')
#                 print(f'BEGIN_AMOUNT: {initial_amount}')
#                 print(f'PROFIT: {diff}')
#                 print(f'TOTAL IN CYCLE: {total}')
#                 print('----------------******----------------\n\n')
#
#
#     return 'task completed'

from decimal import Decimal

from celery import shared_task

from process.CachedClient import CachedClient
from .config import chains, AMOUNT, THRESHOLD, REPEAT_TIMES, DEBUG
from .enum import OrderType
from .utils import to_pairs, number_to_decimal
import time

pairs_dict = {}

# def fill_dict(coins_chain: str, pairs: dict):
#     pairs[coins_chain] = to_pairs(coins_chain)


@shared_task
def start_trading():
    client = CachedClient()
    start_time = time.time()
    prices = client.get_binance_prices()
    print(f'prices: {prices}, exec_time: {time.time() - start_time}')

    # [fill_dict(chain, pairs_dict) for chain in chains]
    print(f'chains: {chains}')
    total = 0.0
    for _ in range(1):
        for pairs in chains:
            coeff = number_to_decimal(1)
            idx = 0
            for pair, order in pairs:
                price = prices[pair]
                print(f'pair: {pair} price: {price}, idx: {idx}')
                if order == OrderType.BUY:
                    coeff *= (number_to_decimal(1) / price)
                else:
                    coeff *= price

                idx += 1


                # if idx == 0:
                #     coeff = coeff * (number_to_decimal(1)/price)
                # else:


            diff = coeff - 1
            print(f'pairs: {pairs}, coeff: {coeff}, diff: {diff}, threshold: {THRESHOLD}, trade: {diff >= THRESHOLD}')
            traded = False
            if diff >= THRESHOLD:
                traded = True
                if DEBUG:
                    print(f'---------------------')
                    print(f'found profitable pair')
                    print(f'key: {pairs}, diff: {diff}')
                    print(f'---------------------')
                else:
                    idx = 0
                    initial_amount = AMOUNT
                    qty = AMOUNT
                    trade_result = 0.0

                    for pair, order in pairs:
                        if order == OrderType.BUY:
                            order, err_msg = client.create_buy_order(pair, qty)
                        else:
                            order, err_msg = client.create_sell_order(pair, qty)

                        if order is None:
                            raise ValueError(err_msg)

                        order = client.check_order(order=order, symbol=pair)
                        print(f'order: {order}')
                        if order is None:
                            raise ValueError('Order check is failed')
                        if order == OrderType.SELL:
                            qty = float(order['executedQty'])
                        else:
                            qty = float(order['cummulativeQuoteQty'])

                        if idx == len(pairs) - 1:
                            trade_result = qty
                            print('traded successfully')

                        idx += 1

                    if traded:
                        diff = trade_result - initial_amount
                        total += diff
                        print('----------------******----------------\n\n')
                        print(f'BEGIN_AMOUNT: {initial_amount}')
                        print(f'PROFIT: {diff}')
                        print(f'TOTAL IN CYCLE: {total}')
                        print('----------------******----------------\n\n')

    # buy_order = client.create_buy_order(symbol='BTCUSDT', amount=200)
    # print(f'buy_order: {buy_order}')
    # sell_order = client.create_sell_order(symbol='DOGEBTC', amount=291.0)
    # print(f'sell_order: {sell_order}')
    #
    #
    #
    # return ''

    # total: float = 0
    # for _ in range(REPEAT_TIMES):
    #     for chain in chains:
    #         pairs = to_pairs(chain)
    #         begin_amount = Decimal(AMOUNT)
    #         result = Decimal('0')
    #
    #         coeff =  (number_to_decimal(100) - number_to_decimal(FEE)) / number_to_decimal(100) # 0.999
    #
    #         for [idx, pair] in enumerate(pairs):
    #             price = number_to_decimal(client.get_last_price_of_symbol(symbol=pair))
    #             print(f'ticker: {pair} {price} {result}')
    #
    #             if idx == 0:
    #                 result = begin_amount / price
    #             else:
    #                 result *= price
    #
    #             result *= coeff
    #         # 50.5
    #         diff = result - begin_amount
    #         # (0.5 / 50)
    #         calc_threshold = (diff / begin_amount) * number_to_decimal(100)
    #
    #         print(f''
    #               f'calculated_result: {result} USDT,'
    #               f'diff: {diff} USDT,'
    #               f'calc_threshold: {calc_threshold}%,'
    #               f'threshold: {THRESHOLD}%,'
    #               f'isTrade: {calc_threshold > number_to_decimal(THRESHOLD)}'
    #             )
    #
    #         if DEBUG:
    #             continue
    #
    #         traded = False
    #
    #         initial_amount = AMOUNT
    #         qty = AMOUNT
    #         trade_result = 0.0
    #
    #         if calc_threshold > number_to_decimal(THRESHOLD): # ratio
    #             traded = True
    #
    #             for [idx, symbol] in enumerate(pairs):
    #                 print(f'symbol: {symbol}')
    #                 is_buy = idx == 0
    #                 if is_buy:
    #                     order, err_msg = client.create_buy_order(symbol=symbol, amount=qty)
    #                 else:
    #                     order, err_msg = client.create_sell_order(symbol=symbol, amount=qty)
    #
    #                 if order is None:
    #                     raise ValueError(err_msg)
    #
    #                 order = client.check_order(order=order, symbol=symbol)
    #
    #                 if order is None:
    #                     raise ValueError('Order check is failed')
    #                 if is_buy:
    #                     qty = float(order['executedQty'])
    #                 else:
    #                     qty = float(order['cummulativeQuoteQty'])
    #
    #                 if idx == len(pairs) - 1:
    #                     trade_result = qty
    #                     print('traded successfully')
    #
    #         if traded:
    #             diff = trade_result - initial_amount
    #             total += diff
    #             print('----------------******----------------\n\n')
    #             print(f'BEGIN_AMOUNT: {initial_amount}')
    #             print(f'PROFIT: {diff}')
    #             print(f'TOTAL IN CYCLE: {total}')
    #             print('----------------******----------------\n\n')


    return 'task completed'