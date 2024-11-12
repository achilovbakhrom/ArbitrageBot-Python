from enum import Enum


class OrderType(Enum):
    BUY = 'buy'
    SELL = 'sell'

    def __str__(self):
        return self.value