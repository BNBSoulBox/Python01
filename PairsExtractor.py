import databutton as db
import streamlit as st
import requests

url = "https://api.coingecko.com/api/v3/exchanges/binance/tickers"
response = requests.get(url)

if response.status_code == 200: # Get the response data as a dictionary 
    data = response.json() # Print the response data

    # Extract the tickers from the response data
    tickers = data["tickers"]
    formatted_pairs = []
    
    for ticker in tickers:
        base = ticker["base"]
        target = ticker["target"]
        formatted_pair = base + target
        formatted_pairs.append(formatted_pair)


    st.write(formatted_pairs)   

else: 
    st.write("Error: Failed to retrieve data from the API")
