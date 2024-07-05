import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

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
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df.fillna(method='ffill', inplace=True)
    return df

# Upload CSV files
uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True, type="csv")
if uploaded_files:
    raw_data = load_data(uploaded_files)
    st.write("Raw Data", raw_data)

    # Preprocess the data
    data = preprocess_data(raw_data)
    st.write("Preprocessed Data", data)
    
    # Feature Engineering
    data['return'] = data['close'].pct_change()
    data['volatility'] = data['return'].rolling(window=30).std()
    data['momentum'] = data['close'] - data['close'].shift(30)
    data.dropna(inplace=True)

    st.write("Feature Engineered Data", data)

    # Train-test split
    X = data[['return', 'volatility', 'momentum']]
    y = data['close'].shift(-1).dropna()
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

    # Arbitrage Detection
    data['rf_pred'] = rf_model.predict(scaler.transform(data[['return', 'volatility', 'momentum']].fillna(0)))
    data['lr_pred'] = lr_model.predict(scaler.transform(data[['return', 'volatility', 'momentum']].fillna(0)))
    data['signal'] = np.where(data['rf_pred'] > data['close'], 1, -1)  # Buy signal if prediction > current price
    st.write("Arbitrage Signals", data[['close', 'rf_pred', 'lr_pred', 'signal']])

    # Option to download the results
    csv_buffer = io.StringIO()
    data.to_csv(csv_buffer)
    csv_data = csv_buffer.getvalue()
    st.download_button(
        label="Download Arbitrage Signals as CSV",
        data=csv_data,
        file_name='arbitrage_signals.csv',
        mime='text/csv'
    )
else:
    st.write("Please upload CSV files to start the analysis.")
