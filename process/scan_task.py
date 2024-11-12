from celery import shared_task

from .config import THRESHOLD

import os
import requests
from collections import defaultdict

from .enum import OrderType

# Thresholds for trading volume and price change percentage (volatility)
MIN_VOLUME = 1000  # Minimum 24-hour trading volume (adjust as needed)
MIN_VOLATILITY = 0.5  # Minimum 24-hour price change percentage (adjust as needed)


def get_binance_symbols():
    url = 'https://api.binance.com/api/v1/exchangeInfo'
    response = requests.get(url)
    data = response.json()
    pairs = [(symbol['baseAsset'], symbol['quoteAsset'], symbol['symbol']) for symbol in data['symbols']]
    return pairs


def build_trade_pairs_map(symbols):
    trade_map = defaultdict(set)
    for base, quote, _ in symbols:
        trade_map[base].add(quote)
        trade_map[quote].add(base)  # Assume bidirectional trading for simplification
    return trade_map


def generate_triangular_arbitrage_chains(trade_map):
    triangular_chains = []
    for A in trade_map:
        for B in trade_map[A]:
            for C in trade_map[B]:
                if C in trade_map[A] and A != B and B != C and A != C:
                    triangular_chains.append((A, B, C))
    return triangular_chains


def get_binance_prices_and_volatility():
    url = 'https://api.binance.com/api/v3/ticker/24hr'
    response = requests.get(url)
    data = response.json()

    # Build dictionaries for prices, volumes, and volatility
    prices = {}
    volume_data = {}
    volatility_data = {}

    for item in data:
        symbol = item['symbol']
        prices[symbol] = float(item['lastPrice'])
        volume_data[symbol] = float(item['volume'])
        volatility_data[symbol] = abs(float(item['priceChangePercent']))  # absolute change percentage

    return prices, volume_data, volatility_data


def find_arbitrage_opportunities(symbols, prices, volumes, volatility, chains):
    arbitrage_opportunities = []

    for A, B, C in chains:
        try:
            # Form pairs for the chain
            pair1 = f"{A}{B}" if f"{A}{B}" in prices else f"{B}{A}"
            pair2 = f"{B}{C}" if f"{B}{C}" in prices else f"{C}{B}"
            pair3 = f"{C}{A}" if f"{C}{A}" in prices else f"{A}{C}"

            # Check volume and volatility for each pair
            # if (
            #         volumes.get(pair1, 0) >= MIN_VOLUME and
            #         volumes.get(pair2, 0) >= MIN_VOLUME and
            #         volumes.get(pair3, 0) >= MIN_VOLUME and
            #         volatility.get(pair1, 0) >= MIN_VOLATILITY and
            #         volatility.get(pair2, 0) >= MIN_VOLATILITY and
            #         volatility.get(pair3, 0) >= MIN_VOLATILITY
            # ):

                # Get prices and invert if necessary
            if prices[pair1] > 0 and prices[pair2] > 0 and prices[pair3] > 0:
                x1, o1 = (prices[pair1], OrderType.SELL) if pair1 == f"{A}{B}" else (1 / prices[pair1], OrderType.BUY)  # Sell A to buy B
                x2, o2 = (prices[pair2], OrderType.SELL) if pair2 == f"{B}{C}" else (1 / prices[pair2], OrderType.BUY)  # Buy C using B
                x3, o3 = (prices[pair3], OrderType.SELL) if pair3 == f"{C}{A}" else (1 / prices[pair3], OrderType.BUY)  # Buy A using C

                # Check for arbitrage opportunity
                if x1 * x2 * x3 > 1 + THRESHOLD:
                    profit_ratio = x1 * x2 * x3
                    arbitrage_opportunities.append({
                        "chain": [(pair1, o1.value), (pair2, o2.value), (pair3, o3.value)],
                        "rate": profit_ratio
                    })
        except KeyError:
            continue  # Skip if any price data is missing

    return arbitrage_opportunities


def get_next_filename(prefix="opportunities/output", extension=".txt"):
    i = 1
    while os.path.exists(f"{prefix}-{i}{extension}"):
        i += 1
    return f"{prefix}-{i}{extension}"


def save_to_file(filename, opportunities):
    with open(filename, 'w') as file:
        for opportunity in opportunities:
            file.write(
                f"Arbitrage Opportunity: Chain = {opportunity['chain']}, Profit Ratio = {opportunity['rate']:.4f}\n")


@shared_task
def start_scan():
    symbols = get_binance_symbols()
    print('sss', symbols)
    prices, volumes, volatility = get_binance_prices_and_volatility()
    trade_map = build_trade_pairs_map(symbols)
    print('trade_map', trade_map, prices)
    triangular_chains = generate_triangular_arbitrage_chains(trade_map)
    # print('triangular_chains', triangular_chains)
    arbitrage_opportunities = find_arbitrage_opportunities(symbols, prices, volumes, volatility, triangular_chains)

    # Determine the output filename and save results
    output_filename = get_next_filename()
    save_to_file(output_filename, arbitrage_opportunities)

    return 'task completed'