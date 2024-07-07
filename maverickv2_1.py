import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import io

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense
except ImportError as e:
    st.error(f"TensorFlow import error: {e}")
    st.stop()
except Exception as e:
    st.error(f"Unexpected error during TensorFlow import: {e}")
    st.stop()

# Set the page config
st.set_page_config(page_title="Crypto Arbitrage Analysis", page_icon="🪙", layout="wide", initial_sidebar_state="expanded")

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
        # Handle any rows where parsing failed
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

        # Model Training
        st.write("Training Models...")

        # Random Forest Model
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train_scaled, y_train)
        y_pred_rf = rf_model.predict(X_test_scaled)

        # Linear Regression Model
        lr_model = LinearRegression()
        lr_model.fit(X_train_scaled, y_train)
        y_pred_lr = lr_model.predict(X_test_scaled)

        # Evaluation
        rf_mse = mean_squared_error(y_test, y_pred_rf)
        lr_mse = mean_squared_error(y_test, y_pred_lr)

        st.write(f"Random Forest MSE: {rf_mse}")
        st.write(f"Linear Regression MSE: {lr_mse}")

        # Visualization
        plt.figure(figsize=(10, 5))
        plt.plot(y_test.index, y_test, label='Actual')
        plt.plot(y_test.index, y_pred_rf, label='Random Forest Predictions')
        plt.plot(y_test.index, y_pred_lr, label='Linear Regression Predictions')
        plt.legend()
        st.pyplot(plt)

        # Adding LSTM Model
        X_train_lstm = X_train_scaled.reshape((X_train_scaled.shape[0], X_train_scaled.shape[1], 1))
        X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], X_test_scaled.shape[1], 1))
        
        lstm_model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(X_train_lstm.shape[1], 1)),
            LSTM(50),
            Dense(1)
        ])
        lstm_model.compile(optimizer='adam', loss='mse')
        lstm_model.fit(X_train_lstm, y_train, epochs=50, batch_size=32, validation_data=(X_test_lstm, y_test))

        y_pred_lstm = lstm_model.predict(X_test_lstm)
        lstm_mse = mean_squared_error(y_test, y_pred_lstm)
        
        st.write(f"LSTM Model MSE: {lstm_mse}")

        # Visualization with LSTM
        plt.figure(figsize=(10, 5))
        plt.plot(y_test.index, y_test, label='Actual')
        plt.plot(y_test.index, y_pred_rf, label='Random Forest Predictions')
        plt.plot(y_test.index, y_pred_lr, label='Linear Regression Predictions')
        plt.plot(y_test.index, y_pred_lstm, label='LSTM Predictions')
        plt.legend()
        st.pyplot(plt)

        # Arbitrage Detection
        data['rf_pred'] = rf_model.predict(scaler.transform(data[['return', 'volatility', 'momentum']].fillna(0)))
        data['lr_pred'] = lr_model.predict(scaler.transform(data[['return', 'volatility', 'momentum']].fillna(0)))
        lstm_input = scaler.transform(data[['return', 'volatility', 'momentum']].fillna(0)).reshape((data.shape[0], 3, 1))
        data['lstm_pred'] = lstm_model.predict(lstm_input).flatten()
        
        data['rf_diff'] = np.abs(data['Momentum Score'] - data['rf_pred'])
        data['lr_diff'] = np.abs(data['Momentum Score'] - data['lr_pred'])
        data['lstm_diff'] = np.abs(data['Momentum Score'] - data['lstm_pred'])
        
        data['signal'] = np.where(data['lstm_pred'] > data['Momentum Score'], 1, -1)  # Buy signal if prediction > current price
        
        # Filter by the latest date and then sort by the smallest difference to select top 20 results
        latest_date = data.index.max()
        recent_data = data[data.index.date == latest_date.date()]
        display_data = recent_data.sort_values(by=['lstm_diff']).head(20)
        
        st.write("Top 20 Arbitrage Signals",
