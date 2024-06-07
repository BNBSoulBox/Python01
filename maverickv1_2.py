import streamlit as st
import csv
import pandas as pd
import numpy as np
from tradingview_ta import TA_Handler, Interval, Exchange

# Function to fetch data using TradingView TA Handler
def fetch_all_data(symbol, exchange, screener, interval):
    try:
        handler = TA_Handler(
            symbol=symbol,
            exchange=exchange,
            screener=screener,
            interval=interval,
            timeout=None
        )
        analysis = handler.get_analysis()
        return analysis
    except Exception as e:
        return None

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

# Function to calculate balanced recommendation score for BUY/SELL balance
def calculate_balanced_recommendation(data, timeframes):
    scores = {
        'BUY': 1,
        'SELL': -1
    }

    total_buy = total_sell = 0
    weight_sum = 0

    for (symbol, interval), analysis in data.items():
        if analysis is None:
            continue
        summary = analysis.summary
        weight = timeframes[interval]

        total_buy += summary['BUY'] * scores['BUY'] * weight
        total_sell += summary['SELL'] * scores['SELL'] * weight
        weight_sum += weight

    if weight_sum == 0:
        return float('inf')

    average_buy = total_buy / weight_sum
    average_sell = total_sell / weight_sum

    return abs(average_buy - average_sell)

# Main function
def main():
    st.title('Crypto Analysis with TradingView TA')

    # List of symbols to analyze
    symbols = [
        "BTCUSDT", "ETHUSDT", "BTCUSDC", "USDCUSDT", "ETHUSDC", "SOLUSDT", "STETHUSDT", 
        "PEPEUSDT", "DOGEUSDT", "USDEUSDT", "XRPUSDT", "ETHBTC", "MNTUSDT", "WBTCBTC", 
        "TONUSDT", "LTCUSDT", "SOLUSDC", "WUSDT", "BNBUSDT", "LINKUSDT", "MATICUSDT", 
        "APTUSDT", "USDEUSDC", "ADAUSDT", "APEXUSDT", "SHIBUSDT", "ONDOUSDT", "OPUSDT", 
        "TRXUSDT", "NEARUSDT", "AVAXUSDT", "JUPUSDT", "ATOMUSDT", "PYTHUSDT", "LDOUSDT", 
        "FTMUSDT", "BLURUSDT", "MONUSDT", "NOTUSDT", "RNDRUSDT", "EOSUSDT", "KASUSDT", 
        "STRKUSDT", "DAIUSDT", "WLDUSDT", "INJUSDT", "FLOWUSDT", "FLOKIUSDT", "FETUSDT", 
        "AAVEUSDT", "ETHFIUSDT", "SUIUSDT", "TIAUSDT", "ICPUSDT", "ENAUSDT", "FILUSDT", 
        "USDCEUR", "ARUSDT", "BTCEUR", "STXUSDT", "HLGUSDT", "RUNEUSDT", "TAIKOUSDT", 
        "BONKUSDT", "SANDUSDT", "ZETAUSDT", "XRPEUR", "DOTUSDT", "HBARUSDT", "WIFUSDT", 
        "CAKEUSDT", "ENSUSDT", "GALAUSDT", "XRPUSDC", "APEUSDT", "ARBUSDT", "FLTUSDT", 
        "JTOUSDT", "ORDIUSDT", "AGIXUSDT", "IDUSDT", "ALGOUSDT", "ETHEUR", "XLMUSDT", 
        "BRETTUSDT", "ETCUSDT", "SEIUSDT", "PEOPLEUSDT", "CRVUSDT", "PYUSDUSDT", 
        "UNIUSDT", "CYBERUSDT", "HNTUSDT", "ULTIUSDT", "ARKMUSDT", "LTCEUR", "CHZUSDT", 
        "AEVOUSDT", "DEGENUSDT", "MASKUSDT", "WAVES-USDT", "DYDX-USDT", "XRP-USDC", 
        "DOGE-USDC", "PORTAL-USDT", "GALA-USDT", "MANA-USDT", "CRV-USDT", "ELIX-USDT", 
        "ALT-USDT", "CTC-USDT", "SEI-USDT", "CYBER-USDT", "GMT-USDT", "IMX-USDT", 
        "CORE-USDT", "CAKE-USDT", "SOL-BTC", "JASMY-USDT", "ROUTE-USDT", "GRT-USDT", 
        "ADA-EUR", "SOLO-USDT", "HNT-USDT", "TUSD-USDT", "ETH-USDE", "VENOM-USDT", 
        "WOO-USDT", "NYAN-USDT", "TWT-USDT", "LFT-USDT", "MATIC-USDC", "LMWR-USDT", 
        "LTC-EUR", "OMNI-USDT", "SOL-EUR", "ULTI-USDT", "PENDLE-USDT", "DYM-USDT", 
        "MNT-USDC", "WBTC-USDT", "FOXY-USDT", "SNX-USDT", "TOKEN-USDT", "BRETT-USDT", 
        "MAGIC-USDT", "BB-USDT", "MANTA-USDT", "CELO-USDT", "KARATE-USDT", "HFT-USDT", 
        "TNSR-USDT", "FIRE-USDT", "LUNA-USDT", "GMX-USDT", "SUI-USDC", "AVAX-USDC", 
        "XDC-USDT", "EGLD-USDT", "MINA-USDT", "OP-USDC", "VANRY-USDT", "SOL-USDE", 
        "SSV-USDT", "AXL-USDT", "RVN-USDT", "C98-USDT", "BOBA-USDT", "KMNO-USDT", 
        "KAVA-USDT", "INTX-USDT", "ZRX-USDT", "STG-USDT", "BEAM-USDT", "SEI-USDC", 
        "MAVIA-USDT", "PRIME-USDT", "VELAR-USDT", "FLIP-USDT", "DOT-USDC", "ADA-USDC", 
        "FLR-USDT", "ANKR-USDT", "XAI-USDT", "ZERO-USDT", "NUTS-USDT", "YFI-USDT", 
        "PARAM-USDT", "SHRAP-USDT", "TRX-USDC", "LUNC-USDT", "ROSE-USDT", "SAFE-USDT", 
        "MOVR-USDT", "AURY-USDT", "WEN-USDT", "WLD-USDC", "ZIL-USDT", "QTUM-USDT", 
        "CHZ-USDC"
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

    timeframes = {
        '5m': 0.1,
        '15m': 0.2,
        '30m': 0.3,
        '1h': 0.4,
        '2h': 0.5,
        '4h': 0.6,
        '1d': 0.7
    }

    if st.button("Run The Wheel"):
        data = {}
        for symbol in symbols:
            for interval in intervals:
                analysis = fetch_all_data(symbol, exchange, screener, interval)
                if analysis:
                    data[(symbol, interval_str_map[interval])] = analysis

        if data:
            save_to_csv(data)
            st.success('Data has been saved to coin_analysis_data.csv')
            st.download_button(
                label="Download CSV",
                data=open('coin_analysis_data.csv').read(),
                file_name='coin_analysis_data.csv',
                mime='text/csv'
            )

            average_scores = {symbol: calculate_balanced_recommendation({(s, i): data[(s, i)] for (s, i) in data if s == symbol}, timeframes) for symbol in symbols}

            # Filter out symbols that don't have enough data
            average_scores = {symbol: score for symbol, score in average_scores.items() if score != float('inf')}

            # Sort symbols by their balanced recommendation score
            sorted_scores = sorted(average_scores.items(), key=lambda item: item[1])

            if sorted_scores:
                st.write("Coins with Balanced BUY/SELL Recommendations:")
                for symbol, score in sorted_scores:
                    st.write(f"{symbol}: {score}")
            else:
                st.write("Relájate y Peinate")

if __name__ == "__main__":
    main()
