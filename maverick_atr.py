import streamlit as st
import pandas as pd
import numpy as np
from tradingview_ta import TA_Handler, Interval
import csv

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
    
    for interval, df in data[symbol].items():
        if not df.empty and 'high' in df and 'low' in df and 'close' in df and 'volume' in df:
            true_range = calculate_true_range(df['high'], df['low'], df['close'])
            weighted_tr = true_range * df['volume']
            atr_data.append(weighted_tr.sum())
            volume_data.append(df['volume'].sum())
    
    if sum(volume_data) == 0:
        return None  # No volume data available to calculate weighted ATR
    
    weighted_atr = sum(atr_data) / sum(volume_data)
    return weighted_atr

# Streamlit app
def main():
    st.title('Crypto Weighted ATR Analysis')

    # User input for symbols
    user_symbols = st.text_input("Enter symbols (comma separated):")
    if user_symbols:
        symbols = [symbol.strip() for symbol in user_symbols.split(',')]

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
        error_symbols = set()

        for symbol in symbols:
            for interval in intervals:
                try:
                    analysis = fetch_all_data(symbol, exchange, screener, interval)
                    indicators = analysis.indicators
                    volume = indicators.get('volume')
                    high = indicators.get('high')
                    low = indicators.get('low')
                    close = indicators.get('close')

                    if volume is not None and high is not None and low is not None and close is not None:
                        df = pd.DataFrame({
                            'volume': [volume],
                            'high': [high],
                            'low': [low],
                            'close': [close]
                        })
                        data[symbol][interval_str_map[interval]] = df
                    else:
                        data[symbol][interval_str_map[interval]] = pd.DataFrame()
                        error_symbols.add(symbol)
                except Exception:
                    data[symbol][interval_str_map[interval]] = pd.DataFrame()
                    error_symbols.add(symbol)

        results = []

        for symbol in symbols:
            weighted_atr = calculate_weighted_atr(data, symbol)
            if weighted_atr is not None:
                results.append({"Symbol": symbol, "Weighted ATR": weighted_atr})
            else:
                results.append({"Symbol": symbol, "Weighted ATR": "No volume data"})

        results_df = pd.DataFrame(results)
        st.write("Weighted ATR for the requested symbols:")
        st.table(results_df)

        # Button to download the CSV file
        if st.button("Download CSV Data"):
            # Save data to CSV
            with open('coin_analysis_data.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Symbol', 'Interval', 'Category', 'Indicator', 'Value'])
                for symbol in symbols:
                    for interval, df in data[symbol].items():
                        if not df.empty:
                            for index, row in df.iterrows():
                                for column, value in row.items():
                                    writer.writerow([symbol, interval, 'Indicators', column, value])

            st.success('Data has been saved to coin_analysis_data.csv')
            st.download_button(
                label="Download CSV",
                data=open('coin_analysis_data.csv').read(),
                file_name='coin_analysis_data.csv',
                mime='text/csv'
            )

        # Print any errors encountered
        if error_symbols:
            st.write("Some symbols encountered errors and could not fetch complete data.")

if __name__ == "__main__":
    main()
