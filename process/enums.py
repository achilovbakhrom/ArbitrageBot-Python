from enum import Enum

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
    MKR = 'MKR'
    QNT = 'QNT'
    LINK = 'LINK'
    TRY = 'TRY'
    TRX = 'TRX'
    BCH = 'BCH'
    FTM = 'FTM'
    LTC = 'LTC'

    def __str__(self) -> str:
        return self.value


class InternalOrderType(Enum):
    BUY = 'BUY'
    SELL = 'SELL'