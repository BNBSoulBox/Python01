import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from tradingview_ta import TA_Handler, Interval
import csv
import altair as alt

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

# Function to calculate TDFI
def calculate_tdfi(data, symbol):
    td_data = {}
    
    for interval, df in data[symbol].items():
        if not df.empty and 'close' in df:
            close = df['close']
            diff_close = close.diff()
            pos_trend = diff_close.where(diff_close > 0, 0).sum()
            neg_trend = diff_close.where(diff_close < 0, 0).sum()
            td_data[interval] = pos_trend + abs(neg_trend)
    
    return td_data

# Function to calculate weighted TDFI using Pearson method
def calculate_weighted_tdfi(data, symbol):
    td_data = calculate_tdfi(data, symbol)
    intervals = list(td_data.keys())
    td_values = list(td_data.values())
    
    correlations = pd.DataFrame(index=intervals, columns=intervals)
    
    for tf1 in intervals:
        for tf2 in intervals:
            if tf1 != tf2:
                try:
                    corr_values = pearsonr([td_data[tf1]], [td_data[tf2]])[0]
                    correlations.loc[tf1, tf2] = corr_values
                except ValueError:
                    correlations.loc[tf1, tf2] = 0
            else:
                correlations.loc[tf1, tf2] = 1.0
    
    weights = correlations.mean(axis=1)
    weighted_td = sum(weights[tf] * td_data[tf] for tf in intervals if tf in td_data) / sum(weights)
    
    return weighted_td

# Streamlit app
def main():
    st.title('Crypto Weighted ATR and TDFI Analysis')

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
                        for pivot in [
                            'Pivot.M.Classic.Middle', 
                            'Pivot.M.Fibonacci.Middle', 
                            'Pivot.M.Camarilla.Middle', 
                            'Pivot.M.Woodie.Middle', 
                            'Pivot.M.Demark.Middle'
                        ]:
                            if pivot in indicators:
                                df[pivot] = [indicators[pivot]]
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
            weighted_td = calculate_weighted_tdfi(data, symbol)
            if weighted_atr is not None:
                results.append({"Symbol": symbol, "Weighted ATR": weighted_atr, "Weighted TDFI": weighted_td})
            else:
                results.append({"Symbol": symbol, "Weighted ATR": "No volume data", "Weighted TDFI": "No volume data"})

        results_df = pd.DataFrame(results)
        st.write("Weighted ATR and TDFI for the requested symbols:")
        st.table(results_df)

        # Calculate and display Weighted Pivot Points
        timeframes = list(interval_str_map.values())
        weighted_pivot = calculate_weighted_pivot(data, timeframes)
        atr_values = {symbol: calculate_weighted_atr(data, symbol) for symbol in symbols}

        for symbol in symbols:
            atr_value = atr_values.get(symbol, 0)
            if atr_value:
                entry_point, exit_point, safety_range = set_grid_bot_parameters(weighted_pivot, atr_value)
                upper_limit, lower_limit, grid_profit = calculate_additional_metrics(weighted_pivot, atr_value, safety_range)
                
                st.subheader(f'{symbol}')
                metrics_data = {
                    "Metric": [
                        "Weighted Pivot Point", "Entry Point", "Exit Point", "Safety Range",
                        "Upper Limit", "Lower Limit", "Grid Profit (%)"
                    ],
                    "Value": [
                        weighted_pivot, entry_point, exit_point, safety_range,
                        upper_limit, lower_limit, f'{grid_profit:.2f}%'
                    ]
                }
                results_table = pd.DataFrame(metrics_data)
                st.table(results_table)
                
                # Create and display the chart
                chart = create_chart(symbol, metrics_data)
                st.altair_chart(chart, use_container_width=True)

        # Button to download the CSV file
        if st.button("Download CSV Data"):
            save_to_csv(data)
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
