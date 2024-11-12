from .enums import Coin
from decimal import Decimal

def to_pairs(arg: str) -> [str]:
    SPLITTER = '-'
    BASE_COIN = Coin.USDT

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

def number_to_decimal(arg: float):
    return Decimal(str(arg))