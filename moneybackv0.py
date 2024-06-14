import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from tradingview_ta import TA_Handler, Interval
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

# Exponential Moving Average
def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

# Triple Exponential Moving Average
def tema(series, span):
    ema1 = ema(series, span)
    ema2 = ema(ema1, span)
    ema3 = ema(ema2, span)
    return (3 * ema1) - (3 * ema2) + ema3

# Calculate the Moving Average based on the mode
def calculate_ma(mode, series, span):
    if mode == "ema":
        return ema(series, span)
    elif mode == "wma":
        weights = np.arange(1, span + 1)
        return series.rolling(window=span).apply(lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)
    elif mode == "swma":
        return series.rolling(window=span).mean()
    elif mode == "vwma":
        weights = series * series.rolling(window=span).sum()
        return series.rolling(window=span).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
    elif mode == "hull":
        wma_half = calculate_ma("wma", series, span // 2)
        wma_full = calculate_ma("wma", series, span)
        return calculate_ma("wma", (2 * wma_half - wma_full), int(np.sqrt(span)))
    elif mode == "tema":
        return tema(series, span)
    else:
        return series.rolling(window=span).mean()

# Function to calculate TDFI
def calculate_tdfi(price_series, lookback, mma_length, mma_mode, smma_length, smma_mode, n_length):
    price_series = price_series * 1000  # Scaling price as in Pine Script
    mma = calculate_ma(mma_mode, price_series, mma_length)
    smma = calculate_ma(smma_mode, mma, smma_length)
    impetmma = mma.diff()
    impetsmma = smma.diff()
    divma = (mma - smma).abs()
    averimpet = (impetmma + impetsmma) / 2
    tdf = divma * (averimpet ** n_length)
    tdf_normalized = tdf / tdf.abs().rolling(window=lookback * n_length).max()
    return tdf_normalized

# Function to calculate weighted TDFI using Pearson correlation
def calculate_weighted_tdfi(data, intervals):
    tdfi_values = {interval: data[interval].dropna() for interval in intervals}
    correlations = pd.DataFrame(index=intervals, columns=intervals)
    
    for tf1 in intervals:
        for tf2 in intervals:
            if tf1 != tf2:
                try:
                    corr_values = pearsonr(tdfi_values[tf1], tdfi_values[tf2])[0]
                    correlations.loc[tf1, tf2] = corr_values
                except ValueError:
                    correlations.loc[tf1, tf2] = 0
            else:
                correlations.loc[tf1, tf2] = 1.0

    weights = correlations.mean(axis=1)
    weighted_tdfi = sum(weights[tf] * tdfi_values[tf].mean() for tf in intervals if len(tdfi_values[tf]) > 0) / sum(weights)
    
    return weighted_tdfi

# Function to set grid bot parameters
def set_grid_bot_parameters(weighted_tdfi, atr, safety_margin=0.5):
    optimal_range = 2 * atr
    safety_range = optimal_range * (1 + safety_margin)
    entry_point = weighted_tdfi - (optimal_range / 2)
    exit_point = weighted_tdfi + (optimal_range / 2)
    return entry_point, exit_point, safety_range

# Streamlit app
def main():
    st.title('Crypto Weighted TDFI and Grid Bot Parameters')

    user_symbols = st.text_input("Enter symbols (comma separated):")
    if user_symbols:
        symbols = [symbol.strip() for symbol in user_symbols.split(',')]
        
        exchange = "BINANCE"
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
                    if 'close' in indicators:
                        close_prices = pd.Series(indicators['close'])
                        data[symbol][interval_str_map[interval]] = close_prices
                    else:
                        data[symbol][interval_str_map[interval]] = pd.Series(dtype='float64')
                        error_symbols.add(symbol)
                except Exception:
                    data[symbol][interval_str_map[interval]] = pd.Series(dtype='float64')
                    error_symbols.add(symbol)

        results = []

        for symbol in symbols:
            st.subheader(f'Symbol: {symbol}')
            
            tdfi_data = {}
            for interval in intervals:
                df = data[symbol].get(interval_str_map[interval])
                if not df.empty:
                    tdfi_data[interval_str_map[interval]] = calculate_tdfi(df, 13, 13, "ema", 13, "ema", 3)
                    st.write(f"Interval: {interval_str_map[interval]}")
                    st.line_chart(tdfi_data[interval_str_map[interval]])

            weighted_tdfi = calculate_weighted_tdfi(tdfi_data, interval_str_map.values())
            st.write(f"Weighted TDFI: {weighted_tdfi}")

            atr = df.std()  # Placeholder for ATR calculation, replace with actual ATR function if available
            entry_point, exit_point, safety_range = set_grid_bot_parameters(weighted_tdfi, atr)
            st.write(f"Entry Point: {entry_point}, Exit Point: {exit_point}, Safety Range: {safety_range}")

            results.append({"Symbol": symbol, "Weighted TDFI": weighted_tdfi, "Entry Point": entry_point, "Exit Point": exit_point, "Safety Range": safety_range})

        results_df = pd.DataFrame(results)
        st.write("Weighted TDFI and Grid Bot Parameters for the requested symbols:")
        st.table(results_df)

        if error_symbols:
            st.write("Some symbols encountered errors and could not fetch complete data.")

if __name__ == "__main__":
    main()
