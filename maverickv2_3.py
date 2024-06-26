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

# List of symbols to be analyzed, each appended with ".P"
symbols = [
    "10000LADYSUSDT.P", "10000NFTUSDT.P", "1000BONKUSDT.P", "1000BTTUSDT.P", 
    "1000FLOKIUSDT.P", "1000LUNCUSDT.P", "1000PEPEUSDT.P", "1000XECUSDT.P", 
    "1INCHUSDT.P", "AAVEUSDT.P", "ACHUSDT.P", "ADAUSDT.P", "AGIXUSDT.P", 
    "AGLDUSDT.P", "AKROUSDT.P", "ALGOUSDT.P", "ALICEUSDT.P", "ALPACAUSDT.P", 
    "ALPHAUSDT.P", "AMBUSDT.P", "ANCUSDT.P", "ANKRUSDT.P", "ANTUSDT.P", 
    "APEUSDT.P", "API3USDT.P", "APTUSDT.P", "ARUSDT.P", "ARBUSDT.P", "ARKUSDT.P", 
    "ARKMUSDT.P", "ARPAUSDT.P", "ASTRUSDT.P", "ATAUSDT.P", "ATOMUSDT.P", 
    "AUCTIONUSDT.P", "AUDIOUSDT.P", "AVAXUSDT.P", "AXSUSDT.P", "BADGERUSDT.P", 
    "BAKEUSDT.P", "BALUSDT.P", "BANDUSDT.P", "BATUSDT.P", "BCHUSDT.P", 
    "BELUSDT.P", "BICOUSDT.P", "BIGTIMEUSDT.P", "BITUSDT.P", "BLURUSDT.P", "BLZUSDT.P",
    "BUSDUSDT.P", "C98USDT.P", "CEEKUSDT.P", "CELOUSDT.P", "CELRUSDT.P", "CFXUSDT.P",
    "CHRUSDT.P", "CHZUSDT.P", "CKBUSDT.P", "COCOSUSDT.P", "COMBOUSDT.P", "COMPUSDT.P",
    "COREUSDT.P", "COTIUSDT.P", "CREAMUSDT.P", "CROUSDT.P", "CRVUSDT.P", "CTCUSDT.P",
    "CTKUSDT.P", "CTSIUSDT.P", "CVCUSDT.P", "CVXUSDT.P", "CYBERUSDT.P", "DARUSDT.P",
    "DASHUSDT.P", "DENTUSDT.P", "DGBUSDT.P", "DODOUSDT.P", "DOGEUSDT.P", "DOTUSDT.P",
    "DUSKUSDT.P", "DYDXUSDT.P", "EDUUSDT.P", "EGLDUSDT.P", "ENJUSDT.P", "ENSUSDT.P",
    "EOSUSDT.P", "ETCUSDT.P", "ETHUSDT.P", "ETHWUSDT.P", "FETUSDT.P", "FILUSDT.P",
    "FITFIUSDT.P", "FLOWUSDT.P", "FLRUSDT.P", "FORTHUSDT.P", "FRONTUSDT.P", "FTMUSDT.P",
    "FTTUSDT.P", "FXSUSDT.P", "GALUSDT.P", "GALAUSDT.P", "GFTUSDT.P", "GLMUSDT.P",
    "GLMRUSDT.P", "GMTUSDT.P", "GMXUSDT.P", "GPTUSDT.P", "GRTUSDT.P", "GSTUSDT.P",
    "GTCUSDT.P", "HBARUSDT.P", "HFTUSDT.P", "HIFIUSDT.P", "HIGHUSDT.P", "HNTUSDT.P",
    "HOOKUSDT.P", "HOTUSDT.P", "ICPUSDT.P", "ICXUSDT.P", "IDUSDT.P", "IDEXUSDT.P",
    "ILVUSDT.P", "IMXUSDT.P", "INJUSDT.P", "IOSTUSDT.P", "IOTAUSDT.P", "IOTXUSDT.P",
    "JASMYUSDT.P", "JOEUSDT.P", "JSTUSDT.P", "KASUSDT.P", "KAVAUSDT.P", "KDAUSDT.P",
    "KEYUSDT.P", "KLAYUSDT.P", "KNCUSDT.P", "KSMUSDT.P", "LDOUSDT.P", "LEVERUSDT.P",
    "LINAUSDT.P", "LINKUSDT.P", "LITUSDT.P", "LOOKSUSDT.P", "LOOMUSDT.P", "LPTUSDT.P",
    "LQTYUSDT.P", "LRCUSDT.P", "LTCUSDT.P", "LUNAUSDT.P", "LUNA2USDT.P", "MAGICUSDT.P",
    "MANAUSDT.P", "MASKUSDT.P", "MATICUSDT.P", "MAVUSDT.P", "MCUSDT.P", "MDTUSDT.P",
    "MINAUSDT.P", "MKRUSDT.P", "MNTUSDT.P", "MTLUSDT.P", "MULTIUSDT.P", "NEARUSDT.P",
    "NEOUSDT.P", "NKNUSDT.P", "NMRUSDT.P", "NTRNUSDT.P", "OCEANUSDT.P", "OGUSDT.P",
    "OGNUSDT.P", "OMGUSDT.P", "ONEUSDT.P", "ONTUSDT.P", "OPUSDT.P", "ORBSUSDT.P",
    "ORDIUSDT.P", "OXTUSDT.P", "PAXGUSDT.P", "PENDLEUSDT.P", "PEOPLEUSDT.P", "PERPUSDT.P",
    "PHBUSDT.P", "PROMUSDT.P", "QNTUSDT.P", "QTUMUSDT.P", "RADUSDT.P", "RAYUSDT.P",
    "RDNTUSDT.P", "REEFUSDT.P", "RENUSDT.P", "REQUSDT.P", "RLCUSDT.P", "RNDRUSDT.P",
    "ROSEUSDT.P", "RPLUSDT.P", "RSRUSDT.P", "RSS3USDT.P", "RUNEUSDT.P", "RVNUSDT.P",
    "SANDUSDT.P", "SCUSDT.P", "SCRTUSDT.P", "SEIUSDT.P", "SFPUSDT.P", "SHIB1000USDT.P",
    "SKLUSDT.P", "SLPUSDT.P", "SNXUSDT.P", "SOLUSDT.P", "SPELLUSDT.P", "SRMUSDT.P",
    "SSVUSDT.P", "STGUSDT.P", "STMXUSDT.P", "STORJUSDT.P", "STPTUSDT.P", "STRAXUSDT.P",
    "STXUSDT.P", "SUIUSDT.P", "SUNUSDT.P", "SUSHIUSDT.P", "SWEATUSDT.P", "SXPUSDT.P",
    "TUSDT.P", "THETAUSDT.P", "TLMUSDT.P", "TOMIUSDT.P", "TOMOUSDT.P", "TONUSDT.P",
    "TRBUSDT.P", "TRUUSDT.P", "TRXUSDT.P", "TWTUSDT.P", "UMAUSDT.P", "UNFIUSDT.P",
    "UNIUSDT.P", "USDCUSDT.P", "USTUSDT.P", "VETUSDT.P", "VGXUSDT.P", "VRAUSDT.P",
    "WAVESUSDT.P", "WAXPUSDT.P", "WLDUSDT.P", "WOOUSDT.P", "WSMUSDT.P", "XCNUSDT.P",
    "XEMUSDT.P", "XLMUSDT.P", "XMRUSDT.P", "XNOUSDT.P", "XRPUSDT.P", "XTZUSDT.P",
    "XVGUSDT.P", "XVSUSDT.P", "YFIUSDT.P", "YFIIUSDT.P", "YGGUSDT.P", "ZBCUSDT.P",
    "ZECUSDT.P", "ZENUSDT.P", "ZILUSDT.P", "ZRXUSDT.P"
]

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
    st.title('#MaryBot - Simbolos para Estrategia de Cobertura')

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
                        lower_bound = weighted_bb_media * 0.99
                        upper_bound = weighted_bb_media * 1.01
                        if lower_bound <= current_price <= upper_bound:
                            percentage = ((current_price - weighted_bb_media) / weighted_bb_media) * 100
                            matches.append({
                                "Symbol": symbol,
                                "Current Price": current_price,
                                "Weighted BB Media": weighted_bb_media,
                                "Percentage": percentage
                            })

            if matches:
                df = pd.DataFrame(matches)
                df = df.sort_values(by="Percentage").reset_index(drop=True)
                df.index += 1  # Start index from 1
                df.index.name = 'Index'
                st.write("Symbols with Current Price within ±1% range of the Weighted Bollinger Bands Media:")
                
                def color_percentage(val):
                    if val <= -0.51:
                        color = 'green'
                    elif -0.5 <= val <= 0.5:
                        color = 'grey'
                    elif val >= 0.51:
                        color = 'red'
                    else:
                        color = 'black'
                    return f'color: {color}'

                styled_df = df.style.applymap(color_percentage, subset=['Percentage'])
                st.table(styled_df)

                # Option to download filtered DataFrame
                csv = df.to_csv().encode('utf-8')
                st.download_button(
                    label="Download Filtered Data as CSV",
                    data=csv,
                    file_name='filtered_data.csv',
                    mime='text/csv'
                )
                
                # Option to print filtered DataFrame
                if st.button("Print Filtered Data"):
                    st.write(styled_df)
            else:
                st.write("No Matches")

def valen_bot():
    st.title("#ValenBot")

    # Add your ValenBot code here or any other functionality for this page

if page == "Home":
    home()
elif page == "ValenBot":
    valen_bot()
