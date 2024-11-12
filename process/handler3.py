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
from redis.commands.search.reducers import count

from process.CachedClient import CachedClient
from .config import chains, AMOUNT, THRESHOLD, REPEAT_TIMES, DEBUG
from .utils import to_pairs, number_to_decimal
from concurrent.futures import ThreadPoolExecutor, as_completed

FEE = 0.1 # % BINANCE FEE

pairs_dict = {}

def fill_dict(coins_chain: str, pairs: dict):
    pairs[coins_chain] = to_pairs(coins_chain)

def get_last_prices(client: CachedClient, pairs: [str]):


    with ThreadPoolExecutor() as executor:
        requests = [
            executor.submit(client.get_last_price_of_symbol, pair)
            for pair in pairs
        ]
        prices = {}
        for future in as_completed(requests):
            result = future.result()
            prices.update(result)

    return prices


@shared_task
def start_trading():
    client = CachedClient()
    [fill_dict(chain, pairs_dict) for chain in chains]
    print(f'dict: {pairs_dict}')
    for _ in range(3):
        for key, pairs in pairs_dict.items():
            print(f'key, value: {key}, {pairs}')
            prices = []
            with ThreadPoolExecutor() as executor:
                requests = [
                    executor.submit(client.get_last_price_of_symbol, symbol)
                    for symbol in pairs
                ]

                for future in as_completed(requests):
                    result = future.result()
                    prices.append(result)

            coeff = 1
            for price in prices:
                if price[0] == pairs[0]:
                    coeff = coeff * (1/price[1])
                else:
                    coeff = coeff * price[1]

            print(f'prices: {prices}')


            diff = coeff - 1
            print(f'key: {key}, coeff: {coeff}, diff: {diff}, threshold: {THRESHOLD}, trade: {diff >= THRESHOLD}')
            if diff >= THRESHOLD:
                print(f'---------------------')
                print(f'found profitable pair')
                print(f'key: {key}, diff: {diff}')
                print(f'---------------------')


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