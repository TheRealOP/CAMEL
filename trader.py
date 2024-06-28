import os
import pandas as pd
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import time

# Alpaca API credentials
API_KEY = 'PKBFVVJTCA8UROJJVG5K'
API_SECRET = 'YX1S6spa859Zd6tf9PckwZWxAULx3CceEyYFF4Wg'
CSV_FILE = 'crypto_data.csv'
CURRENTLY_TRADING = True

# Alpaca Client
trading_client = TradingClient(API_KEY, API_SECRET, paper=True)


def read_csv_data(csv_file):
    df = pd.read_csv(csv_file)
    return df


def get_moving_averages(df, window_short=12, window_long=26):
    if len(df) < window_long:
        print("Not enough data to calculate moving averages.")
        return df, None, None
    df['short_avg'] = df['price'].rolling(window=window_short).mean()
    df['long_avg'] = df['price'].rolling(window=window_long).mean()
    return df, df['short_avg'].iloc[-1], df['long_avg'].iloc[-1]


def trade(symbol, df):
    print('trading')
    df, short_avg, long_avg = get_moving_averages(df)
    if short_avg is None or long_avg is None:
        return

    last_row = df.iloc[-1]

    try:
        position = trading_client.get_open_position('BTCUSD')
    except Exception:
        position = None

    account = trading_client.get_account()
    cash = float(account.cash)

    if short_avg > long_avg and not position and cash >= 1:
        qty = float(cash / last_row['price'])
        qty/=2
        if qty > 0:
            market_order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC
            )
            trading_client.submit_order(order_data=market_order_data)
            print(f"Placed BUY order for {qty} {symbol} at {last_row['price']}")
    elif short_avg < long_avg and position:
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=position.qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.GTC
        )
        trading_client.submit_order(order_data=market_order_data)
        print(f"Placed SELL order for {position.qty} {symbol} at {last_row['price']}")
    else:
        print("No trade executed.", short_avg,long_avg, position)


def start_trading():
    symbol = 'BTC/USD'
    while CURRENTLY_TRADING:
        try:
            df = read_csv_data(CSV_FILE)
            trade(symbol, df)
            time.sleep(60)  # Check every minute
        except Exception as e:
            print(e)
            break


def stop_trading():
    trading_client.close_all_positions(cancel_orders=True)

# Start the trading algorithm
if __name__ == '__main__':
    start_trading()

# To stop the trading algorithm, call stop_trading()
