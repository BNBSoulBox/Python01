import streamlit as st
import csv
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from tradingview_ta import TA_Handler, Interval

# Fetch data using TradingView TA Handler
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

# Save fetched data to a CSV file
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

# Calculate weighted pivot points
def calculate_weighted_pivot(data, timeframes):
    pivot_columns = ['Pivot.M.Classic.Middle', 'Pivot.M.Fibonacci.Middle', 'Pivot.M.Camarilla.Middle', 'Pivot.M.Woodie.Middle', 'Pivot.M.Demark.Middle']
    pivot_data = {tf: [] for tf in timeframes}

    for (symbol, interval), analysis in data.items():
        if analysis is None:
            continue
        interval_str = interval.split('_')[1].lower()
        pivot_values = [analysis.indicators.get(pivot, 0) for pivot in pivot_columns]
        pivot_data[interval_str].append(np.mean(pivot_values))

    correlations = pd.DataFrame(index=timeframes, columns=timeframes)
    for tf1 in timeframes:
        for tf2 in timeframes:
            if tf1 != tf2:
                corr_values = [pearsonr(pivot_data[tf1], pivot_data[tf2])[0] for pivot in pivot_columns]
                correlations.loc[tf1, tf2] = np.mean(corr_values)
            else:
                correlations.loc[tf1, tf2] = 1.0

    weights = correlations.mean(axis=1)
    weighted_pivot = sum(weights[tf] * np.mean(pivot_data[tf]) for tf in timeframes) / sum(weights)

    return weighted_pivot

# Set grid bot parameters
def set_grid_bot_parameters(weighted_pivot, atr, safety_margin=0.5):
    optimal_range = 2 * atr
    safety_range = optimal_range * (1 + safety_margin)
    entry_point = weighted_pivot - (optimal_range / 2)
    exit_point = weighted_pivot + (optimal_range / 2)
    
    return entry_point, exit_point, safety_range

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

    if st.button("Fetch Data"):
        data = {}
        for symbol in symbols:
            for interval in intervals:
                try:
                    analysis = fetch_all_data(symbol, exchange, screener, interval)
                    data[(symbol, interval)] = analysis
                except Exception as e:
                    st.error(f"Error fetching data for {symbol} at interval {interval}: {e}")
                    data[(symbol, interval)] = None

        if data:
            save_to_csv(data)
            st.success('Data has been saved to coin_analysis_data.csv')
            st.download_button(
                label="Download CSV",
                data=open('coin_analysis_data.csv').read(),
                file_name='coin_analysis_data.csv',
                mime='text/csv'
            )

            timeframes = ['5m', '15m', '30m', '1h', '2h', '4h', '1d']
            weighted_pivot = calculate_weighted_pivot(data, timeframes)
            atr_value = 0.002  # Ejemplo de valor ATR, debe calcularse en base a los datos reales
            entry_point, exit_point, safety_range = set_grid_bot_parameters(weighted_pivot, atr_value)

            st.write(f'Weighted Pivot Point: {weighted_pivot}')
            st.write(f'Entry Point: {entry_point}')
            st.write(f'Exit Point: {exit_point}')
            st.write(f'Safety Range: {safety_range}')

if __name__ == "__main__":
    main()
