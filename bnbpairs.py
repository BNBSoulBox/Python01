import requests
import json
import streamlit as st

# Create a Streamlit page
st.title("Binance Futures Trading Pairs List")

# Fetch Binance futures trading pairs list
url = "https://fapi.binance.com/fapi/v1/exchangeInfo"  # Binance futures API endpoint
response = requests.get(url)
data = response.json()

# Initialize trading_pairs variable
trading_pairs = []

# Check if the response is successful
if 'symbols' in data:
    # Extract trading pairs from response
    trading_pairs = [pair['symbol'] for pair in data['symbols']]

    # Save trading pairs as a JSON file
    file_name = "binance_futures_trading_pairs.json"
    with open(file_name, 'w') as file:
        json.dump(trading_pairs, file)

    # Print success message
    st.success(f"The Binance futures trading pairs list has been saved as {file_name}.")
else:
    st.error("Error fetching trading pairs. Please try again.")

# Display the trading pairs
st.write("Trading Pairs:")
for pair in trading_pairs:
    st.write(pair)
