import requests

from binance import Client
from binance.exceptions import BinanceAPIException

from .config import API_KEY, API_SECRET, DEBUG
from .enums import InternalOrderType
from decimal import Decimal, ROUND_DOWN



class CachedClient:
    def __init__(self):
        self.client = Client(testnet=DEBUG, api_key=API_KEY, api_secret=API_SECRET)
        self.cache: dict = {}

    def get_symbol_info(self, symbol: str):
        """Fetches balance of the asset in the account."""
        cached = self.cache.get(symbol)
        if cached is not None:
            return cached

        try:
            cached = self.client.get_symbol_info(symbol=symbol)
            self.cache[symbol] = cached
            return cached
        except BinanceAPIException as e:
            print(f"Error fetching balance for {symbol}: {e}")
            return None

    def get_base_asset(self, symbol: str):
        FIELD_NAME = 'baseAsset'
        cached = self.cache.get(symbol)
        if cached is not None:
            return cached.get(FIELD_NAME)

        try:
            cached = self.client.get_symbol_info(symbol=symbol)
            self.cache[symbol] = cached
            return cached.get(FIELD_NAME)
        except BinanceAPIException as e:
            print(f"Error fetching symbol info for {symbol}: {e}")
            return None

    def get_quote_asset(self, symbol: str):
        FIELD_NAME = 'quoteAsset'
        cached = self.cache.get(symbol)
        if cached is not None:
            return cached.get(FIELD_NAME)

        try:
            cached = self.client.get_symbol_info(symbol=symbol)
            self.cache[symbol] = cached
            return cached.get(FIELD_NAME)
        except BinanceAPIException as e:
            print(f"Error fetching symbol info for {symbol}: {e}")
            return None

    def get_asset_balance(self, asset: str):
        """Fetches balance of the asset in the account."""
        try:
            balance_info = self.client.get_asset_balance(asset=asset)
            return float(balance_info['free'])
        except BinanceAPIException as e:
            print(f"Error fetching balance for {asset}: {e}")
            return 0.0

    def get_last_price_of_symbol(self, symbol: str):
        try:
            ticker = self.client.get_ticker(symbol=symbol)
            price = float(ticker["lastPrice"])
            print(f'symbol: {symbol}, price: {price}')
            return symbol, price
        except BinanceAPIException as e:
            print(f"Error fetching ticker info for {symbol}: {e}")
            return 0.0

    def get_binance_prices(self):
        url = 'https://api.binance.com/api/v3/ticker/price'
        response = requests.get(url)
        data = response.json()
        prices = [(item['symbol'][:3], item['symbol'][3:], item['price']) for item in data]
        symbol_dict = {f"{base}{quote}": Decimal(price) for base, quote, price in prices}
        return symbol_dict

    # Before creation of order need to check followings
    # 1. Check Balance
    # 2. Handle API Errors

    def create_buy_order(self, symbol: str, amount: float):
        return self._create_order_internal(InternalOrderType.BUY, symbol=symbol, amount=amount)

    def create_sell_order(self, symbol: str, amount: float):
        return self._create_order_internal(InternalOrderType.SELL, symbol=symbol, amount=amount)

    def _create_order_internal(self, order_type: InternalOrderType, symbol: str, amount: float):
        if order_type == InternalOrderType.SELL:
            print(f'sell order - symbol: {symbol}, amount: {amount}')
            asset = self.get_base_asset(symbol)
        else:
            print(f'buy order - symbol: {symbol}, amount: {amount}')
            asset = self.get_quote_asset(symbol)

        if asset is None:
            return None, 'Cannot get quote asset'
        # balance = self.get_asset_balance(asset=asset)
        final_amount = Decimal(str(amount))
        # print(f'balance: {balance}, final_amount: {final_amount}')
        # if balance < final_amount:
        #     if 0.95 * final_amount < balance:
        #         final_amount = balance
        #     else:
        #         return None, 'Insufficient funds'
        symbol_info = self.client.get_symbol_info(symbol)
        lot_size = next(filter for filter in symbol_info['filters'] if filter['filterType'] == 'LOT_SIZE')
        min_qty = float(lot_size['minQty'])
        max_qty = float(lot_size['maxQty'])
        step_size = lot_size['stepSize']
        print(f"LOT_SIZE rules - minQty: {min_qty}, maxQty: {max_qty}, stepSize: {step_size}")
        ss = Decimal(step_size)

        # adjusted_amount = final_amount - (final_amount % step_size)
        adjusted_amount = final_amount if ss > final_amount else  (final_amount // ss) * ss
        print(f'sss {adjusted_amount} {final_amount} {ss}')

        adjusted_amount = adjusted_amount.quantize(ss, rounding=ROUND_DOWN)

        # print(f'balance: {balance}, asset: {asset}, final_amount: {final_amount}, adjusted_amount: {adjusted_amount}, type: {order_type}')
        print(f'symbol: {symbol}, final_amount: {final_amount}, adjusted_amount: {adjusted_amount}, type: {order_type}')
        if order_type == InternalOrderType.SELL:
            order = self.client.order_market_sell(symbol=symbol, quantity=float(adjusted_amount))
        else:
            order = self.client.order_market_buy(symbol=symbol, quoteOrderQty=float(adjusted_amount))

        return order, None

    def check_order(self, order: dict, symbol: str):

        temp_order = order

        print(f'temp_order 1: {temp_order}')

        while temp_order['status'] != 'FILLED':
            temp_order = self.client.get_order(symbol=symbol, orderId=order['orderId'])
            print(f'temp_order: {temp_order}')

        print(f'temp_order 2: {temp_order}')

        return temp_order