import streamlit as st
import csv
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from tradingview_ta import TA_Handler, Interval
import ta  # Technical Analysis library for ATR calculation

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

# Function to save data to CSV
def save_to_csv(data, filename='coin_analysis_data.csv'):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Symbol', 'Interval', 'Category', 'Indicator', 'Value'])
        for (symbol, interval), analysis in data.items():
            if analysis is None:
                continue
            summary = analysis.summary
            oscillators = analysis.oscillators
            moving_averages = analysis.moving_averages
            indicators = analysis.indicators

            writer.writerow([symbol, interval, 'Summary', 'RECOMMENDATION', summary['RECOMMENDATION']])
            writer.writerow([symbol, interval, 'Summary', 'BUY', summary['BUY']])
            writer.writerow([symbol, interval, 'Summary', 'SELL', summary['SELL']])
            writer.writerow([symbol, interval, 'Summary', 'NEUTRAL', summary['NEUTRAL']])

            writer.writerow([symbol, interval, 'Oscillators', 'RECOMMENDATION', oscillators['RECOMMENDATION']])
            for key, value in oscillators['COMPUTE'].items():
                writer.writerow([symbol, interval, 'Oscillators', key, value])

            writer.writerow([symbol, interval, 'Moving Averages', 'RECOMMENDATION', moving_averages['RECOMMENDATION']])
            for key, value in moving_averages['COMPUTE'].items():
                writer.writerow([symbol, interval, 'Moving Averages', key, value])

            for key, value in indicators.items():
                writer.writerow([symbol, interval, 'Indicators', key, value])

# Function to calculate weighted pivot point
def calculate_weighted_pivot(data, timeframes):
    pivot_columns = ['Pivot.M.Classic.Middle', 'Pivot.M.Fibonacci.Middle', 'Pivot.M.Camarilla.Middle', 'Pivot.M.Woodie.Middle', 'Pivot.M.Demark.Middle']
    pivot_data = {tf: [] for tf in timeframes}

    for (symbol, interval), analysis in data.items():
        if analysis is None:
            continue
        interval_str = interval
        pivot_values = [analysis.indicators.get(pivot, 0) for pivot in pivot_columns]
        pivot_data[interval_str].append(np.mean(pivot_values))

    correlations = pd.DataFrame(index=timeframes, columns=timeframes)
    for tf1 in timeframes:
        for tf2 in timeframes:
            if tf1 != tf2:
                try:
                    if len(pivot_data[tf1]) >= 2 and len(pivot_data[tf2]) >= 2:
                        corr_values = pearsonr(pivot_data[tf1], pivot_data[tf2])[0]
                        correlations.loc[tf1, tf2] = corr_values
                    else:
                        correlations.loc[tf1, tf2] = 0
                except ValueError:
                    correlations.loc[tf1, tf2] = 0  # Set correlation to 0 if not enough data
            else:
                correlations.loc[tf1, tf2] = 1.0

    weights = correlations.mean(axis=1)
    weighted_pivot = sum(weights[tf] * np.mean(pivot_data[tf]) for tf in timeframes if len(pivot_data[tf]) > 0) / sum(weights)

    return weighted_pivot

# Function to set grid bot parameters
def set_grid_bot_parameters(weighted_pivot, atr, safety_margin=0.5):
    optimal_range = 2 * atr
    safety_range = optimal_range * (1 + safety_margin)
    entry_point = weighted_pivot - (optimal_range / 2)
    exit_point = weighted_pivot + (optimal_range / 2)
    
    return entry_point, exit_point, safety_range

# Function to calculate ATR using the fetched data
def calculate_atr(data):
    high_prices = []
    low_prices = []
    close_prices = []

    for (_, interval), analysis in data.items():
        if analysis is None:
            continue
        indicators = analysis.indicators
        high_prices.append(indicators.get('high', 0))
        low_prices.append(indicators.get('low', 0))
        close_prices.append(indicators.get('close', 0))

    df = pd.DataFrame({
        'high': high_prices,
        'low': low_prices,
        'close': close_prices
    })

    if len(df) < 14:
        return 0

    atr = ta.volatility.AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)
    return atr.average_true_range()[-1]

def main():
    st.title('Crypto Analysis with TradingView TA')
    
    user_input = st.text_input("Enter symbols separated by commas", "BTC,ETH,XRP")
    symbols = [symbol.strip() for symbol in user_input.split(',')]

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

    if st.button("Fetch Data"):
        data = {}
        for symbol in symbols:
            for interval in intervals:
                try:
                    analysis = fetch_all_data(symbol, exchange, screener, interval)
                    data[(symbol, interval_str_map[interval])] = analysis
                except Exception as e:
                    st.error(f"Error fetching data for {symbol} at interval {interval_str_map[interval]}: {e}")
                    data[(symbol, interval_str_map[interval])] = None

        if data:
            save_to_csv(data)
            st.success('Data has been saved to coin_analysis_data.csv')
            st.download_button(
                label="Download CSV",
                data=open('coin_analysis_data.csv').read(),
                file_name='coin_analysis_data.csv',
                mime='text/csv'
            )

            timeframes = list(interval_str_map.values())
            weighted_pivot = calculate_weighted_pivot(data, timeframes)
            atr_value = calculate_atr(data)  # Calculate ATR based on the fetched data
            entry_point, exit_point, safety_range = set_grid_bot_parameters(weighted_pivot, atr_value)

            st.write(f'Weighted Pivot Point: {weighted_pivot}')
            st.write(f'Entry Point: {entry_point}')
            st.write(f'Exit Point: {exit_point}')
            st.write(f'Safety Range: {safety_range}')

if __name__ == "__main__":
    main()
