import streamlit as st
import csv
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from tradingview_ta import TA_Handler, Interval

# List of symbols to be analyzed
symbols = [
    "10000LADYSUSDT", "10000NFTUSDT", "1000BONKUSDT", "1000BTTUSDT", 
    "1000FLOKIUSDT", "1000LUNCUSDT", "1000PEPEUSDT", "1000XECUSDT", 
    "1INCHUSDT", "AAVEUSDT", "ACHUSDT", "ADAUSDT", "AGIXUSDT", 
    "AGLDUSDT", "AKROUSDT", "ALGOUSDT", "ALICEUSDT", "ALPACAUSDT", 
    "ALPHAUSDT", "AMBUSDT", "ANCUSDT", "ANKRUSDT", "ANTUSDT", 
    "APEUSDT", "API3USDT", "APTUSDT", "ARUSDT", "ARBUSDT", "ARKUSDT", 
    "ARKMUSDT", "ARPAUSDT", "ASTRUSDT", "ATAUSDT", "ATOMUSDT", 
    "AUCTIONUSDT", "AUDIOUSDT", "AVAXUSDT", "AXSUSDT", "BADGERUSDT", 
    "BAKEUSDT", "BALUSDT", "BANDUSDT", "BATUSDT", "BCHUSDT", 
    "BELUSDT", "BICOUSDT", "BIGTIMEUSDT", "BITUSDT", "BLURUSDT", "BLZUSDT",
    "BUSDUSDT", "C98USDT", "CEEKUSDT", "CELOUSDT", "CELRUSDT", "CFXUSDT",
    "CHRUSDT", "CHZUSDT", "CKBUSDT", "COCOSUSDT", "COMBOUSDT", "COMPUSDT",
    "COREUSDT", "COTIUSDT", "CREAMUSDT", "CROUSDT", "CRVUSDT", "CTCUSDT",
    "CTKUSDT", "CTSIUSDT", "CVCUSDT", "CVXUSDT", "CYBERUSDT", "DARUSDT",
    "DASHUSDT", "DENTUSDT", "DGBUSDT", "DODOUSDT", "DOGEUSDT", "DOTUSDT",
    "DUSKUSDT", "DYDXUSDT", "EDUUSDT", "EGLDUSDT", "ENJUSDT", "ENSUSDT",
    "EOSUSDT", "ETCUSDT", "ETHUSDT", "ETHWUSDT", "FETUSDT", "FILUSDT",
    "FITFIUSDT", "FLOWUSDT", "FLRUSDT", "FORTHUSDT", "FRONTUSDT", "FTMUSDT",
    "FTTUSDT", "FXSUSDT", "GALUSDT", "GALAUSDT", "GFTUSDT", "GLMUSDT",
    "GLMRUSDT", "GMTUSDT", "GMXUSDT", "GPTUSDT", "GRTUSDT", "GSTUSDT",
    "GTCUSDT", "HBARUSDT", "HFTUSDT", "HIFIUSDT", "HIGHUSDT", "HNTUSDT",
    "HOOKUSDT", "HOTUSDT", "ICPUSDT", "ICXUSDT", "IDUSDT", "IDEXUSDT",
    "ILVUSDT", "IMXUSDT", "INJUSDT", "IOSTUSDT", "IOTAUSDT", "IOTXUSDT",
    "JASMYUSDT", "JOEUSDT", "JSTUSDT", "KASUSDT", "KAVAUSDT", "KDAUSDT",
    "KEYUSDT", "KLAYUSDT", "KNCUSDT", "KSMUSDT", "LDOUSDT", "LEVERUSDT",
    "LINAUSDT", "LINKUSDT", "LITUSDT", "LOOKSUSDT", "LOOMUSDT", "LPTUSDT",
    "LQTYUSDT", "LRCUSDT", "LTCUSDT", "LUNAUSDT", "LUNA2USDT", "MAGICUSDT",
    "MANAUSDT", "MASKUSDT", "MATICUSDT", "MAVUSDT", "MCUSDT", "MDTUSDT",
    "MINAUSDT", "MKRUSDT", "MNTUSDT", "MTLUSDT", "MULTIUSDT", "NEARUSDT",
    "NEOUSDT", "NKNUSDT", "NMRUSDT", "NTRNUSDT", "OCEANUSDT", "OGUSDT",
    "OGNUSDT", "OMGUSDT", "ONEUSDT", "ONTUSDT", "OPUSDT", "ORBSUSDT",
    "ORDIUSDT", "OXTUSDT", "PAXGUSDT", "PENDLEUSDT", "PEOPLEUSDT", "PERPUSDT",
    "PHBUSDT", "PROMUSDT", "QNTUSDT", "QTUMUSDT", "RADUSDT", "RAYUSDT",
    "RDNTUSDT", "REEFUSDT", "RENUSDT", "REQUSDT", "RLCUSDT", "RNDRUSDT",
    "ROSEUSDT", "RPLUSDT", "RSRUSDT", "RSS3USDT", "RUNEUSDT", "RVNUSDT",
    "SANDUSDT", "SCUSDT", "SCRTUSDT", "SEIUSDT", "SFPUSDT", "SHIB1000USDT",
    "SKLUSDT", "SLPUSDT", "SNXUSDT", "SOLUSDT", "SPELLUSDT", "SRMUSDT",
    "SSVUSDT", "STGUSDT", "STMXUSDT", "STORJUSDT", "STPTUSDT", "STRAXUSDT",
    "STXUSDT", "SUIUSDT", "SUNUSDT", "SUSHIUSDT", "SWEATUSDT", "SXPUSDT",
    "TUSDT", "THETAUSDT", "TLMUSDT", "TOMIUSDT", "TOMOUSDT", "TONUSDT",
    "TRBUSDT", "TRUUSDT", "TRXUSDT", "TWTUSDT", "UMAUSDT", "UNFIUSDT",
    "UNIUSDT", "USDCUSDT", "USTUSDT", "VETUSDT", "VGXUSDT", "VRAUSDT",
    "WAVESUSDT", "WAXPUSDT", "WLDUSDT", "WOOUSDT", "WSMUSDT", "XCNUSDT",
    "XEMUSDT", "XLMUSDT", "XMRUSDT", "XNOUSDT", "XRPUSDT", "XTZUSDT",
    "XVGUSDT", "XVSUSDT", "YFIUSDT", "YFIIUSDT", "YGGUSDT", "ZBCUSDT",
    "ZECUSDT", "ZENUSDT", "ZILUSDT", "ZRXUSDT"
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

# Function to calculate weighted pivot points
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
                    corr_values = pearsonr(pivot_data[tf1], pivot_data[tf2])[0]
                    correlations.loc[tf1, tf2] = corr_values
                except ValueError:
                    correlations.loc[tf1, tf2] = 0
            else:
                correlations.loc[tf1, tf2] = 1.0

    weights = correlations.mean(axis=1)
    weighted_pivot = sum(weights[tf] * np.mean(pivot_data[tf]) for tf in timeframes if len(pivot_data[tf]) > 0) / sum(weights)

    return weighted_pivot

# Function to calculate ATR based on extracted data
def calculate_atr(data, intervals):
    atr_values = []
    for (symbol, interval), analysis in data.items():
        if analysis is None:
            continue
        high_prices = analysis.indicators.get('High', [])
        low_prices = analysis.indicators.get('Low', [])
        close_prices = analysis.indicators.get('Close', [])
        if len(high_prices) > 1 and len(low_prices) > 1 and len(close_prices) > 1:
            tr = np.max([np.array(high_prices) - np.array(low_prices),
                         np.abs(np.array(high_prices) - np.array(close_prices[:-1])),
                         np.abs(np.array(low_prices) - np.array(close_prices[:-1]))], axis=0)
            atr = np.mean(tr)
            atr_values.append(atr)
    return np.mean(atr_values) if atr_values else 0

# Function to set grid bot parameters
def set_grid_bot_parameters(weighted_pivot, atr, safety_margin=0.5):
    optimal_range = 2 * atr
    safety_range = optimal_range * (1 + safety_margin)
    entry_point = weighted_pivot - (optimal_range / 2)
    exit_point = weighted_pivot + (optimal_range / 2)
    
    return entry_point, exit_point, safety_range

def main():
    st.title('Crypto Analysis with TradingView TA')
    
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
        errors = []
        for symbol in symbols:
            for interval in intervals:
                try:
                    analysis = fetch_all_data(symbol, exchange, screener, interval)
                    data[(symbol, interval_str_map[interval])] = analysis
                except Exception as e:
                    errors.append(f"{symbol} at interval {interval_str_map[interval]}: {str(e)}")
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
            atr_value = calculate_atr(data, intervals)  # Calculate ATR based on the actual data
            entry_point, exit_point, safety_range = set_grid_bot_parameters(weighted_pivot, atr_value)

            matches = []

            for (symbol, interval), analysis in data.items():
                if analysis:
                    current_price = analysis.indicators.get('close', 0)
                    lower_bound = current_price * 0.999
                    upper_bound = current_price * 1.001
                    if lower_bound <= weighted_pivot <= upper_bound:
                        matches.append(symbol)

            if matches:
                st.write("Symbols with Weighted Pivot Point within 0.1% range of the current price:")
                for match in matches:
                    st.write(match)
            else:
                st.write("No Matches")
        
        else:
            st.warning("No data could be fetched for any symbol.")

if __name__ == "__main__":
    main()
