from .enums import Coin

API_KEY = '3sjnjuuGN5MDtSLGYIr33wLPWUEdpsEA9bU8z5fMC5jxCOV7luZ9JbbNJQrVqO2y'
API_SECRET = '1fjUhtDLg9smjiysSFdfTW6DmZLEGDOkH1DoewzJ4wyK9QdzAJxVG0awSob04WWB'
AMOUNT = 1000 # means $1000

USER_THRESHOLD = 0.0003 # means if THRESHOLD gt 0.3%
BINANCE_SLIPPAGE = 0.001

THRESHOLD = USER_THRESHOLD + BINANCE_SLIPPAGE

REPEAT_TIMES = 100

DEBUG=True

chains = [
    f'{Coin.USDT}-{Coin.AVAX}-{Coin.BTC}-{Coin.USDT}', # usdt - avax - btc - usdt
    f'{Coin.USDT}-{Coin.ETH}-{Coin.BTC}-{Coin.USDT}', # usdt - avax - btc - usdt
    f'{Coin.USDT}-{Coin.XLM}-{Coin.BTC}-{Coin.USDT}', # usdt - xlm - btc - usdt
    f'{Coin.USDT}-{Coin.XRP}-{Coin.BTC}-{Coin.USDT}', # usdt - xrp - btc - usdt
    f'{Coin.USDT}-{Coin.LDO}-{Coin.BTC}-{Coin.USDT}', # usdt - ldo  - btc - usdt
    f'{Coin.USDT}-{Coin.MKR}-{Coin.BTC}-{Coin.USDT}', # usdt - ldo  - btc - usdt
    f'{Coin.USDT}-{Coin.QNT}-{Coin.BTC}-{Coin.USDT}', # usdt - ldo  - btc - usdt
    f'{Coin.USDT}-{Coin.DOGE}-{Coin.BTC}-{Coin.USDT}', # usdt - ldo  - btc - usdt
    f'{Coin.USDT}-{Coin.SHIB}-{Coin.DOGE}-{Coin.BTC}-{Coin.USDT}', # usdt - ldo  - btc - usdt
]