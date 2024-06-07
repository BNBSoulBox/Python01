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
            summary['BUY'] * scores['BUY'] +
            summary['STRONG_BUY'] * scores['STRONG_BUY'] +
            summary['NEUTRAL'] * scores['NEUTRAL'] +
            summary['SELL'] * scores['SELL'] +
            summary['STRONG_SELL'] * scores['STRONG_SELL']
        ) * weights[interval]
        
        total_score += weighted_score
        total_weight += weights[interval]

    average_score = total_score / total_weight if total_weight else 0
    return average_score

def main():
    st.title('Crypto Analysis with TradingView TA')

    # List of symbols to analyze
    symbols = [
        "BTCUSDT", "ETHUSDT", "BTCUSDC", "USDCUSDT", "ETHUSDC", "SOLUSDT", 
        "STETHUSDT", "PEPEUSDT", "DOGEUSDT", "USDEUSDT", "XRPUSDT", "ETHBTC", 
        "MNTUSDT", "WBTCBTC", "TONUSDT", "LTCUSDT", "SOLUSDC", "WUSDT", 
        "BNBUSDT", "LINKUSDT", "MATICUSDT", "APTUSDT", "USDEUSDC", "ADAUSDT", 
        "APEXUSDT", "SHIBUSDT", "ONDOUSDT", "OPUSDT", "TRXUSDT", "NEARUSDT", 
        "AVAXUSDT", "JUPUSDT", "ATOMUSDT", "PYTHUSDT", "LDOUSDT", "FTMUSDT", 
        "BLURUSDT", "MONUSDT", "NOTUSDT", "RNDRUSDT", "EOSUSDT", "KASUSDT", 
        "STRKUSDT", "DAIUSDT", "WLDUSDT", "INJUSDT", "FLOWUSDT", "FLOKIUSDT", 
        "FETUSDT", "AAVEUSDT", "ETHFIUSDT", "SUIUSDT", "TIAUSDT", "ICPUSDT", 
        "ENAUSDT", "FILUSDT", "USDCEUR", "ARUSDT", "BTCEUR", "STXUSDT", 
        "HLGUSDT", "RUNEUSDT", "TAIKOUSDT", "BONKUSDT", "SANDUSDT", "ZETAUSDT", 
        "XRPEUR", "DOTUSDT", "HBARUSDT", "WIFUSDT", "CAKEUSDT", "ENSUSDT", 
        "GALAUSDT", "XRPUSDC", "APEUSDT", "ARBUSDT", "FLTUSDT", "JTOUSDT", 
        "ORDIUSDT", "AGIXUSDT", "IDUSDT", "ALGOUSDT", "ETHEUR", "XLMUSDT", 
        "BRETTUSDT", "ETCUSDT", "SEIUSDT", "PEOPLEUSDT", "CRVUSDT", "PYUSDUSDT", 
        "UNIUSDT", "CYBERUSDT", "HNTUSDT", "ULTIUSDT", "ARKMUSDT", "LTCEUR", 
        "CHZUSDT", "AEVOUSDT", "DEGENUSDT", "MASKUSDT", "WAVESUSDT", "DYDXUSDT", 
        "XRPUSDC", "DOGEUSDC", "PORTALUSDT", "GALAUSDT", "MANAUSDT", "CRVUSDT", 
        "ELIXUSDT", "ALTUSDT", "CTCUSDT", "SEIUSDT", "CYBERUSDT", "GMTUSDT", 
        "IMXUSDT", "COREUSDT", "CAKEUSDT", "SOLBTC", "JASMYUSDT", "ROUTEUSDT", 
        "GRTUSDT", "ADAEUR", "SOLOUSDT", "HNTUSDT", "TUSDUSDT", "ETHUSDE", 
        "VENOMUSDT", "WOOUSDT", "NYANUSDT", "TWTUSDT", "LFTUSDT", "MATICUSDC", 
        "LMWRUSDT", "LTCEUR", "OMNIUSDT", "SOLEUR", "ULTIUSDT", "PENDLEUSDT", 
        "DYMUSDT", "MNTUSDC", "WBTCUSDT", "FOXYUSDT", "SNXUSDT", "TOKENUSDT", 
        "BRETTUSDT", "MAGICUSDT", "BBUSDT", "MANTAUSDT", "CELOUSDT", "KARATEUSDT", 
        "HFTUSDT", "TNSRUSDT", "FIREUSDT", "LUNAUSDT", "GMXUSDT", "SUIUSDC", 
        "AVAXUSDC", "XDCUSDT", "EGLDUSDT", "MINAUSDT", "OPUSDC", "VANRYUSDT", 
        "SOLUSDE", "SSVUSDT", "AXLUSDT", "RVNUSDT", "C98USDT", "BOBAUSDT", 
        "KMNOUSDT", "KAVAUSDT", "INTXUSDT", "ZRXUSDT", "STGUSDT", "BEAMUSDT", 
        "SEIUSDC", "MAVIAUSDT", "PRIMEUSDT", "VELARUSDT", "FLIPUSDT", "DOTUSDC", 
        "ADAUSDC", "FLRUSDT", "ANKRUSDT", "XAIUSDT", "ZEROUSDT", "NUTSUSDT", 
        "YFIUSDT", "PARAMUSDT", "SHRAPUSDT", "TRXUSDC", "LUNCUSDT", "ROSEUSDT", 
        "SAFEUSDT", "MOVRUSDT", "AURYUSDT", "WENUSDT", "WLDUSDC", "ZILUSDT", 
        "QTUMUSDT", "CHZUSDC"
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
