import streamlit as st
import pandas as pd
import numpy as np
from tradingview_ta import TA_Handler, Interval

# Function to fetch data using TradingView TA Handler
def fetch_all_data(symbol, exchange, screener, interval):
    handler = TA_Handler(
        symbol=symbol,
        exchange=exchange,
        screener=screener,
        interval=interval,
        timeout=None
    )
    analysis = handler.get_analysis()
    return analysis

# Function to calculate True Range (TR)
def calculate_true_range(high, low, close):
    previous_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - previous_close).abs()
    tr3 = (low - previous_close).abs()
    true_range = pd.DataFrame({'TR1': tr1, 'TR2': tr2, 'TR3': tr3}).max(axis=1)
    return true_range

# Function to calculate weighted ATR
def calculate_weighted_atr(data, symbol):
    atr_data = []
    volume_data = []
    
    for interval in data[symbol]:
        df = data[symbol][interval]
        if not df.empty:
            true_range = calculate_true_range(df['high'], df['low'], df['close'])
            atr = true_range.rolling(window=14).mean()
            weighted_tr = true_range * df['volume']
            atr_data.append(weighted_tr.sum() / df['volume'].sum())
            volume_data.append(df['volume'].sum())
    
    weighted_atr = sum(atr_data) / sum(volume_data)
    return weighted_atr

# Streamlit app
def main():
    st.title('Crypto Weighted ATR Analysis')

    # User input for symbols
    user_symbols = st.text_input("Enter symbols (comma separated):")
    if user_symbols:
        symbols = [symbol.strip() + ".P" for symbol in user_symbols.split(',')]

        exchange = "BYBIT"
        screener = "crypto"
        intervals = [
            Interval.INTERVAL_5_MINUTES,
            Interval.INTERVAL_15_MINUTES,
            Interval.INTERVAL_30_MINUTES,
            Interval.INTERVAL_1_HOUR,
            Interval.INTERVAL_2_HOURS,
            Interval.INTERVAL_4_HOURS,
            Interval.INTERVAL_1_DAY
        ]

        interval_str_map = {
            Interval.INTERVAL_5_MINUTES: '5m',
            Interval.INTERVAL_15_MINUTES: '15m',
            Interval.INTERVAL_30_MINUTES: '30m',
            Interval.INTERVAL_1_HOUR: '1h',
            Interval.INTERVAL_2_HOURS: '2h',
            Interval.INTERVAL_4_HOURS: '4h',
            Interval.INTERVAL_1_DAY: '1d'
        }

        data = {symbol: {} for symbol in symbols}
        errors = []

        for symbol in symbols:
            for interval in intervals:
                try:
                    analysis = fetch_all_data(symbol, exchange, screener, interval)
                    df = pd.DataFrame(analysis.indicators)
                    df['volume'] = analysis.indicators.get('volume', 0)
                    df['high'] = analysis.indicators.get('high', 0)
                    df['low'] = analysis.indicators.get('low', 0)
                    df['close'] = analysis.indicators.get('close', 0)
                    data[symbol][interval_str_map[interval]] = df
                except Exception as e:
                    data[symbol][interval_str_map[interval]] = pd.DataFrame()
                    errors.append(f"Error fetching data for {symbol} at interval {interval_str_map[interval]}: {e}")

        results = []

        for symbol in symbols:
            weighted_atr = calculate_weighted_atr(data, symbol)
            results.append({"Symbol": symbol, "Weighted ATR": weighted_atr})

        results_df = pd.DataFrame(results)
        st.write("Weighted ATR for the requested symbols:")
        st.table(results_df)

if __name__ == "__main__":
    main()
