import streamlit as st
import csv
from tradingview_ta import TA_Handler, Interval
from flask import Flask, request, jsonify
from threading import Thread

# Initialize Flask app
app = Flask(__name__)

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

def save_to_csv(data, filename='coin_analysis_data.csv'):
    # Create and write to a CSV file
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write headers
        writer.writerow(['Symbol', 'Interval', 'Category', 'Indicator', 'Value'])
        for (symbol, interval), analysis in data.items():
            if analysis is None:
                continue
            summary = analysis.summary
            oscillators = analysis.oscillators
            moving_averages = analysis.moving_averages
            indicators = analysis.indicators

            # Write summary data
            writer.writerow([symbol, interval, 'Summary', 'RECOMMENDATION', summary['RECOMMENDATION']])
            writer.writerow([symbol, interval, 'Summary', 'BUY', summary['BUY']])
            writer.writerow([symbol, interval, 'Summary', 'SELL', summary['SELL']])
            writer.writerow([symbol, interval, 'Summary', 'NEUTRAL', summary['NEUTRAL']])

            # Write oscillators data
            writer.writerow([symbol, interval, 'Oscillators', 'RECOMMENDATION', oscillators['RECOMMENDATION']])
            for key, value in oscillators['COMPUTE'].items():
                writer.writerow([symbol, interval, 'Oscillators', key, value])

            # Write moving averages data
            writer.writerow([symbol, interval, 'Moving Averages', 'RECOMMENDATION', moving_averages['RECOMMENDATION']])
            for key, value in moving_averages['COMPUTE'].items():
                writer.writerow([symbol, interval, 'Moving Averages', key, value])

            # Write indicators data
            for key, value in indicators.items():
                writer.writerow([symbol, interval, 'Indicators', key, value])

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    symbols = data.get('symbols', [])
    exchange = data.get('exchange', "BYBIT")
    screener = data.get('screener', "crypto")
    intervals = data.get('intervals', [
        Interval.INTERVAL_5_MINUTES,
        Interval.INTERVAL_15_MINUTES,
        Interval.INTERVAL_30_MINUTES,
        Interval.INTERVAL_1_HOUR,
        Interval.INTERVAL_2_HOURS,
        Interval.INTERVAL_4_HOURS,
        Interval.INTERVAL_1_DAY
    ])

    result_data = {}
    for symbol in symbols:
        for interval in intervals:
            try:
                analysis = fetch_all_data(symbol, exchange, screener, interval)
                result_data[(symbol, interval)] = analysis
            except Exception as e:
                result_data[(symbol, interval)] = None

    save_to_csv(result_data)
    return jsonify({"message": "Data fetched and saved successfully."}), 200

def main():
    st.title('Crypto Analysis with TradingView TA')
    
    # Get user input
    user_input = st.text_input("Enter symbols separated by commas", "BTC,ETH,XRP")
    symbols = [symbol.strip() for symbol in user_input.split(',')]

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

    if st.button("Fetch Data"):
        data = {}
        for symbol in symbols:
            for interval in intervals:
                try:
                    analysis = fetch_all_data(symbol, exchange, screener, interval)
                    data[(symbol, interval)] = analysis
                except Exception as e:
                    st.error(f"Error fetching data for {symbol} at interval {interval}: {e}")
                    data[(symbol, interval)] = None

        if data:
            save_to_csv(data)
            st.success('Data has been saved to coin_analysis_data.csv')
            st.download_button(
                label="Download CSV",
                data=open('coin_analysis_data.csv').read(),
                file_name='coin_analysis_data.csv',
                mime='text/csv'
            )

def run_flask():
    app.run(port=5000)

if __name__ == "__main__":
    # Run Flask app in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    # Run Streamlit app
    main()
