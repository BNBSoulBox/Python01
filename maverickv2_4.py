import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import io

# Set the page config
st.set_page_config(page_title="Neutral Grid Bot Entry Analysis", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for dark theme and styles
st.markdown("""
    <style>
    .css-18e3th9 { background-color: #0e1117; color: #ffffff; }
    .css-1lcbmhc { background-color: #161a25; }
    .css-1d391kg { color: #ffffff; }
    .stButton>button { color: #ffffff; background-color: #d4af37; border-color: #d4af37; }
    .css-1offfwp e1h7wlp60 { color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# Function to load data from CSV files
def load_data(files):
    data = []
    for file in files:
        df = pd.read_csv(file)
        data.append(df)
    return pd.concat(data, ignore_index=True)

# Function to preprocess data
def preprocess_data(df):
    if 'Fecha' not in df.columns:
        raise KeyError("The required column 'Fecha' is missing from the data.")
    try:
        df['timestamp'] = pd.to_datetime(df['Fecha'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        if df['timestamp'].isnull().any():
            st.warning("Some date formats did not match the expected format and were parsed as NaT.")
            st.write(df[df['timestamp'].isnull()]['Fecha'].head())
            df.dropna(subset=['timestamp'], inplace=True)
    except Exception as e:
        st.error(f"Error parsing dates: {e}")
        st.write("Here are the first few 'Fecha' values for reference:")
        st.write(df['Fecha'].head())
        raise e
    df.set_index('timestamp', inplace=True)
    df.fillna(method='ffill', inplace=True)
    return df

# Upload CSV files
uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True, type="csv")
if uploaded_files:
    raw_data = load_data(uploaded_files)
    st.write("Column Names in Uploaded Data:", raw_data.columns)

    try:
        # Preprocess the data
        data = preprocess_data(raw_data)
        st.write("Preprocessed Data", data)
        
        # Feature Engineering
        data['return'] = data['Momentum Score'].pct_change()
        data['volatility'] = data['return'].rolling(window=30).std()
        data['momentum'] = data['Momentum Score'] - data['Momentum Score'].shift(30)
        data.dropna(inplace=True)

        st.write("Feature Engineered Data", data)

        # Train-test split
        X = data[['return', 'volatility', 'momentum']]
        y = data['Momentum Score'].shift(-1).dropna()
        X = X[:-1]  # Align features with target

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scaling
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # LSTM Model Training
        st.write("Training LSTM Model...")

        # Reshape input to be [samples, time steps, features]
        X_train_reshaped = np.reshape(X_train_scaled, (X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
        X_test_reshaped = np.reshape(X_test_scaled, (X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))

        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=(1, X_train_scaled.shape[1])))
        model.add(LSTM(50))
        model.add(Dense(1))

        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(X_train_reshaped, y_train, epochs=20, batch_size=1, verbose=2)

        # Predictions
        y_pred_lstm = model.predict(X_test_reshaped)
        lstm_mse = mean_squared_error(y_test, y_pred_lstm)

        st.write(f"LSTM Model MSE: {lstm_mse}")

        # Visualization
        plt.figure(figsize=(10, 5))
        plt.plot(y_test.index, y_test, label='Actual')
        plt.plot(y_test.index, y_pred_lstm, label='LSTM Predictions')
        plt.legend()
        st.pyplot(plt)

        # Arbitrage Detection with Entry Conditions
        lstm_input_data = scaler.transform(data[['return', 'volatility', 'momentum']].fillna(0))
        lstm_input_data = np.reshape(lstm_input_data, (lstm_input_data.shape[0], 1, lstm_input_data.shape[1]))
        data['lstm_pred'] = model.predict(lstm_input_data).flatten()
        
        data['lstm_diff'] = np.abs(data['Momentum Score'] - data['lstm_pred'])
        
        # Define thresholds for sustained increasing momentum
        sustained_lower = 0.5
        sustained_upper = 0.7
        
        # Filter for symbols with predicted momentum in the specified range
        filtered_data = data[(data['lstm_pred'] >= sustained_lower) & (data['lstm_pred'] <= sustained_upper)]
        
        # Sort by the smallest difference to select top 20 results
        display_data = filtered_data.sort_values(by='lstm_diff').head(20)
        
        st.write("Top 20 Symbols with Increasing and Sustained Momentum", display_data[['Symbol', 'Momentum Score', 'lstm_pred', 'lstm_diff']])

        # Option to download the results
        csv_buffer = io.StringIO()
        display_data[['Symbol', 'Momentum Score', 'lstm_pred', 'lstm_diff']].to_csv(csv_buffer)
        csv_data = csv_buffer.getvalue()
        st.download_button(
            label="Download Top Symbols as CSV",
            data=csv_data,
            file_name='top_symbols.csv',
            mime='text/csv'
        )
    except KeyError as e:
        st.error(f"Data preprocessing error: {e}")
else:
    st.write("Please upload CSV files to start the analysis.")
