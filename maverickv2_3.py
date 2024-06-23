import streamlit as st
import csv
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from tradingview_ta import TA_Handler, Interval

# Set the page config
st.set_page_config(
    page_title="Trading Analysis",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for dark theme and styles
st.markdown("""
    <style>
    .css-18e3th9 {
        background-color: #0e1117;
        color: #ffffff;
    }
    .css-1lcbmhc {
        background-color: #161a25;
    }
    .css-1d391kg {
        color: #ffffff;
    }
    .stButton>button {
        color: #ffffff;
        background-color: #d4af37;
        border-color: #d4af37;
    }
    .css-1offfwp e1h7wlp60 {
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# Path to the logo
logo_url = "https://raw.githubusercontent.com/BNBSoulBox/Python01/main/canela%20coin.png"

# Sidebar
st.sidebar.image(logo_url, use_column_width=True)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "ValenBot"])

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

# Function to save data to a CSV file
def save_to_csv(data, filename='coin_analysis_data.csv'):
    try:
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
    except Exception as e:
        st.error(f"Error saving data to CSV: {e}")

# Function to calculate weighted Bollinger Bands media
def calculate_weighted_bb_media(data, timeframes):
    bb_lower_column = 'BB.lower'
    bb_upper_column = 'BB.upper'
    bb_data = {tf: [] for tf in timeframes}

    for (symbol, interval), analysis in data.items():
        if analysis is None:
            continue
        interval_str = interval
        bb_lower = analysis.indicators.get(bb_lower_column, 0)
        bb_upper = analysis.indicators.get(bb_upper_column, 0)
        if bb_lower and bb_upper:
            bb_media = (bb_lower + bb_upper) / 2
            bb_data[interval_str].append(bb_media)

    correlations = pd.DataFrame(index=timeframes, columns=timeframes)
    for tf1 in timeframes:
        for tf2 in timeframes:
            if tf1 != tf2:
                try:
                    corr_values = pearsonr(bb_data[tf1], bb_data[tf2])[0]
                    correlations.loc[tf1, tf2] = corr_values
                except ValueError:
                    correlations.loc[tf1, tf2] = 0
            else:
                correlations.loc[tf1, tf2] = 1.0

    weights = correlations.mean(axis=1)
    weighted_bb_media = sum(weights[tf] * np.mean(bb_data[tf]) for tf in timeframes if len(bb_data[tf]) > 0) / sum(weights)

    return weighted_bb_media

def home():
    st.title('#MaryBot - Pares para Estrategia de Cobertura')

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

    matches = []

    if st.button("Has la Magia"):
        data = {}
        errors = []
        for symbol in symbols:
            for interval in intervals:
                try:
                    analysis = fetch_all_data(symbol, exchange, screener, interval)
                    data[(symbol, interval_str_map[interval])] = analysis
                except Exception as e:
                    data[(symbol, interval_str_map[interval])] = None
                    errors.append(f"Error fetching data for {symbol} at interval {interval_str_map[interval]}: {e}")

        if data:
            save_to_csv(data)
            st.success('Data has been saved to coin_analysis_data.csv')
            st.download_button(
                label="Download CSV",
                data=open('coin_analysis_data.csv').read(),
                file_name='coin_analysis_data.csv',
                mime='text/csv'
            )

            weighted_bb_media_dict = {}
            for symbol in symbols:
                timeframes = list(interval_str_map.values())
                weighted_bb_media = calculate_weighted_bb_media({k: v for k, v in data.items() if k[0] == symbol}, timeframes)
                weighted_bb_media_dict[symbol] = weighted_bb_media

            for symbol, weighted_bb_media in weighted_bb_media_dict.items():
                if weighted_bb_media is not None:
                    # Fetch the current price from the 'close' indicator at the 30m interval
                    if (symbol, '30m') in data and data[(symbol, '30m')] is not None:
                        current_price = data[(symbol, '30m')].indicators.get('close', 0)
                        lower_bound = weighted_bb_media * 0.985
                        upper_bound = weighted_bb_media * 1.015
                        if lower_bound <= current_price <= upper_bound:
                            percentage = ((current_price - weighted_bb_media) / weighted_bb_media) * 100
                            matches.append({
                                "Symbol": symbol,
                                "Current Price": current_price,
                                "Weighted BB Media": weighted_bb_media,
                                "Lower Bound": lower_bound,
                                "Upper Bound": upper_bound,
                                "Percentage": percentage
                            })

            if matches:
                df = pd.DataFrame(matches)
                df = df.sort_values(by="Percentage")
                st.write("Simbolos oscilando en el Pivote:")
                st.table(df)
            else:
                st.write("No Manches Wey")

def valen_bot():
    st.title("#ValenBot")

    # Add your ValenBot code here or any other functionality for this page

if page == "Home":
    home()
elif page == "ValenBot":
    valen_bot()
