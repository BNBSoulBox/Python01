import streamlit as st
import csv
import pandas as pd
from tradingview_ta import TA_Handler, Interval, Exchange

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

# Function to calculate weighted recommendation score
def calculate_weighted_recommendation(data, timeframes):
    scores = {
        'STRONG_BUY': 2,
        'BUY': 1,
        'NEUTRAL': 0,
        'SELL': -1,
        'STRONG_SELL': -2
    }
    
    weights = {
        '5m': 0.1,
        '15m': 0.2,
        '30m': 0.3,
        '1h': 0.4,
        '2h': 0.5,
        '4h': 0.6,
        '1d': 0.7
    }

    total_score = 0
    total_weight = 0

    for (symbol, interval), analysis in data.items():
        if analysis is None:
            continue
        
        summary = analysis.summary
        weighted_score = (
            summary.get('BUY', 0) * scores['BUY'] +
            summary.get('STRONG_BUY', 0) * scores['STRONG_BUY'] +
            summary.get('NEUTRAL', 0) * scores['NEUTRAL'] +
            summary.get('SELL', 0) * scores['SELL'] +
            summary.get('STRONG_SELL', 0) * scores['STRONG_SELL']
        ) * weights[interval]
        
        total_score += weighted_score
        total_weight += weights[interval]

    average_score = total_score / total_weight if total_weight else 0
    return average_score

def main():
    st.title('Crypto Analysis with TradingView TA')

    # List of symbols to analyze
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

    if st.button("Run The Wheel"):
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
            average_scores = {symbol: calculate_weighted_recommendation({(s, i): data[(s, i)] for (s, i) in data if s == symbol}, timeframes) for symbol in symbols}

            neutral_recommendations = [symbol for symbol, score in average_scores.items() if -0.5 <= score <= 0.5]

            st.write("Neutral Recommendations:")
            for symbol in neutral_recommendations:
                st.write(symbol)

if __name__ == "__main__":
    main()
