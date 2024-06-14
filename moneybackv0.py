import streamlit as st
import pandas as pd
from scipy.stats import pearsonr
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
    st.title('Crypto Weighted TDFI Analysis')

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
                    close = indicators.get('close')
                    
                    if close is not None:
                        df = pd.DataFrame({'close': [close]})
                        data[symbol][interval_str_map[interval]] = df
                    else:
                        data[symbol][interval_str_map[interval]] = pd.DataFrame()
                        error_symbols.add(symbol)
                except Exception:
                    data[symbol][interval_str_map[interval]] = pd.DataFrame()
                    error_symbols.add(symbol)

        results = []

        for symbol in symbols:
            weighted_td = calculate_weighted_tdfi(data, symbol)
            results.append({"Symbol": symbol, "Weighted TDFI": weighted_td})

        results_df = pd.DataFrame(results)
        st.write("Weighted TDFI for the requested symbols:")
        st.table(results_df)

        # Print any errors encountered
        if error_symbols:
            st.write("Some symbols encountered errors and could not fetch complete data.")

if __name__ == "__main__":
    main()
