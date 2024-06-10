import streamlit as st
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

def main():
    st.title('MAVERICK Hedge Symbols')
    
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

            weighted_bb_media_dict = {}
            for symbol in symbols:
                timeframes = list(interval_str_map.values())
                weighted_bb_media = calculate_weighted_bb_media({k: v for k, v in data.items() if k[0] == symbol}, timeframes)
                weighted_bb_media_dict[symbol] = weighted_bb_media

            matches = []

            for symbol, weighted_bb_media in weighted_bb_media_dict.items():
                if weighted_bb_media is not None:
                    # Fetch the current price from the 'close' indicator at the 30m interval
                    current_price = data[(symbol, '30m')].indicators.get('close', 0)
                    lower_bound = weighted_bb_media * 0.98
                    upper_bound = weighted_bb_media * 1.02
                    if lower_bound <= current_price <= upper_bound:
                        matches.append({
                            "Symbol": symbol,
                            "Current Price": current_price,
                            "Weighted BB Media": weighted_bb_media,
                            "Lower Bound": lower_bound,
                            "Upper Bound": upper_bound
                        })

            if matches:
                df = pd.DataFrame(matches)
                st.write("Symbols with Current Price within 2% range of the Weighted Bollinger Bands Media:")
                st.table(df)
            else:
                st.write("No Matches")
        else:
            st.warning("No data could be fetched for any symbol.")

if __name__ == "__main__":
    main()
