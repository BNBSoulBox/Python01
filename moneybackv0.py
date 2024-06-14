import streamlit as st
from tradingview_ta import TA_Handler, Interval, Exchange
import pandas as pd
import numpy as np

# Function to fetch indicator data
def fetch_indicator_data(symbol, interval):
    handler = TA_Handler(
        symbol=symbol,
        screener="crypto",
        exchange="BINANCE",
        interval=interval
    )
    try:
        analysis = handler.get_analysis()
        return analysis.indicators
    except Exception as e:
        st.error(f"Error fetching data for {symbol} on {interval}: {e}")
        return None

# Function to calculate EMA
def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

# Function to calculate TEMA
def tema(series, span):
    ema1 = ema(series, span)
    ema2 = ema(ema1, span)
    ema3 = ema(ema2, span)
    return (3 * ema1) - (3 * ema2) + ema3

# Function to calculate moving average based on mode
def calculate_ma(mode, series, span):
    if mode == "ema":
        return ema(series, span)
    elif mode == "tema":
        return tema(series, span)
    # Add other modes as required
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
    tdf = (divma ** 1) * (averimpet ** n_length)
    tdf_normalized = tdf / tdf.abs().rolling(window=lookback * n_length).max()
    return tdf_normalized

# Streamlit UI
st.title("Trend Direction Force Index (TDFI) Calculator")

# User inputs
symbol_input = st.text_input("Enter symbol names (comma-separated)", value="BAKEUSDT")
interval = st.selectbox("Select interval", options=[Interval.INTERVAL_5_MINUTES, Interval.INTERVAL_15_MINUTES, Interval.INTERVAL_30_MINUTES, Interval.INTERVAL_1_HOUR, Interval.INTERVAL_2_HOURS, Interval.INTERVAL_4_HOURS, Interval.INTERVAL_1_DAY])

# Parameters
lookback = 13
mma_length = 13
mma_mode = "ema"
smma_length = 13
smma_mode = "ema"
n_length = 3
filter_high = 0.05
filter_low = -0.05

# Process each symbol
symbols = [symbol.strip() for symbol in symbol_input.split(',')]
for symbol in symbols:
    st.subheader(f"Symbol: {symbol}")

    # Fetch data
    data = fetch_indicator_data(symbol, interval)
    if data:
        df = pd.DataFrame(data, index=[0])
        df = df.T
        df.columns = ['Value']
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Indicator'}, inplace=True)

        # Assuming 'close' prices are in the DataFrame under the key 'close'
        if 'close' in df['Indicator'].values:
            price_series = df[df['Indicator'] == 'close']['Value'].astype(float)

            # Calculate TDFI
            tdfi_values = calculate_tdfi(price_series, lookback, mma_length, mma_mode, smma_length, smma_mode, n_length)

            # Apply filtering and generate signals
            signal = tdfi_values.apply(lambda x: 'green' if x > filter_high else 'red' if x < filter_low else 'gray')

            # Create results DataFrame
            results_df = pd.DataFrame({
                'TDFI Value': tdfi_values,
                'Signal': signal
            })

            st.write(results_df)
        else:
            st.warning(f"No 'close' price data available for {symbol}")
    else:
        st.warning(f"Could not fetch data for {symbol}")
