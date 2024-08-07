import streamlit as st
import pandas as pd
import numpy as np
from tradingview_ta import TA_Handler, Interval
from datetime import datetime, timezone, timedelta
import time
import matplotlib.pyplot as plt
import logging
from logging.handlers import RotatingFileHandler
from sqlalchemy import create_engine
from cachetools import TTLCache
from collections import defaultdict

# Set up logging with rotation
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file = 'momentum_dashboard.log'
log_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
log_handler.setFormatter(log_formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# Error aggregation setup
error_counts = defaultdict(int)
last_log_time = time.time()

# Database connection parameters
DB_NAME = "maverick_qhyp"
DB_USER = "maverick_qhyp_user"
DB_PASSWORD = "IEn2tAiSR8rRrkdcQil1irtuOBENel61"
DB_HOST = "dpg-cqh9dneehbks73a6poj0-a.oregon-postgres.render.com"
DB_PORT = "5432"

# Create SQLAlchemy engine
db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(db_url)

# Set up caching
cache = TTLCache(maxsize=1000, ttl=300)  # Cache with 5-minute TTL

# Last cache clear time
last_cache_clear = datetime.now()

# Set the page config
st.set_page_config(
    page_title="Momentum Score Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme and styles
st.markdown("""
    <style>
    .css-18e3th9 {
        background-color: #0e1117;
        color: #ffffff;
    }
    .css-1lcbmhc {
        background-color: #161a25;
    }
    .css-1d391kg {
        color: #ffffff;
    }
    .stButton>button {
        color: #ffffff;
        background-color: #d4af37;
        border-color: #d4af37;
    }
    .css-1offfwp e1h7wlp60 {
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# List of symbols to be analyzed
symbols = [
    "10000LADYSUSDT.P", "10000NFTUSDT.P", "1000BONKUSDT.P", "1000BTTUSDT.P", 
    "1000FLOKIUSDT.P", "1000LUNCUSDT.P", "1000PEPEUSDT.P", "1000XECUSDT.P", 
    "1INCHUSDT.P", "AAVEUSDT.P", "ACHUSDT.P", "ADAUSDT.P", "AGLDUSDT.P", 
    "AKROUSDT.P", "ALGOUSDT.P", "ALICEUSDT.P", "ALPACAUSDT.P", 
    "ALPHAUSDT.P", "AMBUSDT.P", "ANKRUSDT.P", "ANTUSDT.P", 
    "APEUSDT.P", "API3USDT.P", "APTUSDT.P", "ARUSDT.P", "ARBUSDT.P", "ARKUSDT.P", 
    "ARKMUSDT.P", "ARPAUSDT.P", "ASTRUSDT.P", "ATAUSDT.P", "ATOMUSDT.P", 
    "AUCTIONUSDT.P", "AUDIOUSDT.P", "AVAXUSDT.P", "AXSUSDT.P", "BADGERUSDT.P", 
    "BAKEUSDT.P", "BALUSDT.P", "BANDUSDT.P", "BATUSDT.P", "BCHUSDT.P", 
    "BELUSDT.P", "BICOUSDT.P", "BIGTIMEUSDT.P", "BLURUSDT.P", "BLZUSDT.P",
    "BTCUSDT.P", "C98USDT.P", "CEEKUSDT.P", "CELOUSDT.P", "CELRUSDT.P", "CFXUSDT.P",
    "CHRUSDT.P", "CHZUSDT.P", "CKBUSDT.P", "COMBOUSDT.P", "COMPUSDT.P",
    "COREUSDT.P", "COTIUSDT.P", "CROUSDT.P", "CRVUSDT.P", "CTCUSDT.P",
    "CTKUSDT.P", "CTSIUSDT.P", "CVCUSDT.P", "CVXUSDT.P", "CYBERUSDT.P", "DARUSDT.P",
    "DASHUSDT.P", "DENTUSDT.P", "DGBUSDT.P", "DODOUSDT.P", "DOGEUSDT.P", "DOTUSDT.P",
    "DUSKUSDT.P", "DYDXUSDT.P", "EDUUSDT.P", "EGLDUSDT.P", "ENJUSDT.P", "ENSUSDT.P",
    "EOSUSDT.P", "ETCUSDT.P", "ETHUSDT.P", "ETHWUSDT.P", "FILUSDT.P",
    "FITFIUSDT.P", "FLOWUSDT.P", "FLRUSDT.P", "FORTHUSDT.P", "FRONTUSDT.P", "FTMUSDT.P",
    "FXSUSDT.P", "GALAUSDT.P", "GFTUSDT.P", "GLMUSDT.P",
    "GLMRUSDT.P", "GMTUSDT.P", "GMXUSDT.P", "GRTUSDT.P", "GTCUSDT.P", "HBARUSDT.P", 
    "HFTUSDT.P", "HIFIUSDT.P", "HIGHUSDT.P", "HNTUSDT.P",
    "HOOKUSDT.P", "HOTUSDT.P", "ICPUSDT.P", "ICXUSDT.P", "IDUSDT.P", "IDEXUSDT.P",
    "ILVUSDT.P", "IMXUSDT.P", "INJUSDT.P", "IOSTUSDT.P", "IOTAUSDT.P", "IOTXUSDT.P",
    "JASMYUSDT.P", "JOEUSDT.P", "JSTUSDT.P", "KASUSDT.P", "KAVAUSDT.P", "KDAUSDT.P",
    "KEYUSDT.P", "KLAYUSDT.P", "KNCUSDT.P", "KSMUSDT.P", "LDOUSDT.P", "LEVERUSDT.P",
    "LINAUSDT.P", "LINKUSDT.P", "LITUSDT.P", "LOOKSUSDT.P", "LOOMUSDT.P", "LPTUSDT.P",
    "LQTYUSDT.P", "LRCUSDT.P", "LTCUSDT.P", "LUNA2USDT.P", "MAGICUSDT.P",
    "MANAUSDT.P", "MASKUSDT.P", "MATICUSDT.P", "MAVUSDT.P", "MDTUSDT.P",
    "MINAUSDT.P", "MKRUSDT.P", "MNTUSDT.P", "MTLUSDT.P", "NEARUSDT.P",
    "NEOUSDT.P", "NKNUSDT.P", "NMRUSDT.P", "NTRNUSDT.P", "OGUSDT.P",
    "OGNUSDT.P", "OMGUSDT.P", "ONEUSDT.P", "ONTUSDT.P", "OPUSDT.P", "ORBSUSDT.P",
    "ORDIUSDT.P", "OXTUSDT.P", "PAXGUSDT.P", "PENDLEUSDT.P", "PEOPLEUSDT.P", "PERPUSDT.P",
    "PHBUSDT.P", "PROMUSDT.P", "QNTUSDT.P", "QTUMUSDT.P", "RADUSDT.P", "RDNTUSDT.P", 
    "REEFUSDT.P", "RENUSDT.P", "REQUSDT.P", "RLCUSDT.P", "ROSEUSDT.P", 
    "RPLUSDT.P", "RSRUSDT.P", "RSS3USDT.P", "RUNEUSDT.P", "RVNUSDT.P",
    "SANDUSDT.P", "SCUSDT.P", "SCRTUSDT.P", "SEIUSDT.P", "SFPUSDT.P", "SHIB1000USDT.P",
    "SKLUSDT.P", "SLPUSDT.P", "SNXUSDT.P", "SOLUSDT.P", "SPELLUSDT.P", "SSVUSDT.P", 
    "STGUSDT.P", "STMXUSDT.P", "STORJUSDT.P", "STPTUSDT.P", "STXUSDT.P", "SUIUSDT.P", 
    "SUNUSDT.P", "SUSHIUSDT.P", "SWEATUSDT.P", "SXPUSDT.P",
    "TUSDT.P", "THETAUSDT.P", "TLMUSDT.P", "TOMIUSDT.P", "TONUSDT.P",
    "TRBUSDT.P", "TRUUSDT.P", "TRXUSDT.P", "TWTUSDT.P", "UMAUSDT.P", "UNFIUSDT.P",
    "UNIUSDT.P", "USDCUSDT.P", "VETUSDT.P", "VGXUSDT.P", "VRAUSDT.P",
    "WAVESUSDT.P", "WAXPUSDT.P", "WLDUSDT.P", "WOOUSDT.P", "XCNUSDT.P",
    "XEMUSDT.P", "XLMUSDT.P", "XMRUSDT.P", "XNOUSDT.P", "XRPUSDT.P", "XTZUSDT.P",
    "XVGUSDT.P", "XVSUSDT.P", "YFIUSDT.P", "YGGUSDT.P", "ZECUSDT.P", "ZENUSDT.P", "ZILUSDT.P", "ZRXUSDT.P"
]

# Configuration
exchange = "BYBIT"
screener = "crypto"
intervals = {
    Interval.INTERVAL_1_MINUTE: 0.1,
    Interval.INTERVAL_5_MINUTES: 0.1,
    Interval.INTERVAL_15_MINUTES: 0.2,
    Interval.INTERVAL_30_MINUTES: 0.1,
    Interval.INTERVAL_1_HOUR: 0.2,
    Interval.INTERVAL_2_HOURS: 0.1,
    Interval.INTERVAL_4_HOURS: 0.2,
    Interval.INTERVAL_1_DAY: 0.1
}

def log_error(error_message):
    global last_log_time
    error_counts[error_message] += 1
    
    if time.time() - last_log_time > 300:  # Log every 5 minutes
        for error, count in error_counts.items():
            logging.error(f"Error occurred {count} times: {error}")
        error_counts.clear()
        last_log_time = time.time()

@st.cache_data(ttl=3600)
def fetch_all_data(symbol, exchange, screener, interval):
    cache_key = f"{symbol}_{exchange}_{screener}_{interval}"
    if cache_key in cache:
        return cache[cache_key]
    
    try:
        handler = TA_Handler(
            symbol=symbol,
            exchange=exchange,
            screener=screener,
            interval=interval,
            timeout=None
        )
        analysis = handler.get_analysis()
        cache[cache_key] = analysis
        return analysis
    except Exception as e:
        log_error(f"Error fetching data for {symbol} on {interval}: {str(e)}")
        return None

def calculate_momentum_score(data):
    weights = {'STRONG_BUY': 2, 'BUY': 1, 'NEUTRAL': 0, 'SELL': -1, 'STRONG_SELL': -2}
    score = 0
    for interval, analysis in data.items():
        if analysis:
            rating = analysis.summary['RECOMMENDATION'].upper()
            score += weights.get(rating, 0)
    return score

@st.cache_data(ttl=3600)
def get_historical_data():
    query = """
    SELECT * FROM momentum_scores 
    WHERE "Timestamp" >= NOW() - INTERVAL '24 hours'
    ORDER BY "Timestamp" DESC
    """
    return pd.read_sql(query, con=engine, parse_dates=['Timestamp'])

def update_plot(df):
    fig, ax = plt.subplots(figsize=(12, 6))
    
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], utc=True)
    df = df.sort_values('Timestamp')
    
    # Reduce data points by resampling
    df_resampled = df.set_index('Timestamp').resample('5T').mean().reset_index()
    
    avg_momentum = df_resampled['Average Momentum']
    
    for i in range(1, len(avg_momentum)):
        start = df_resampled['Timestamp'].iloc[i-1]
        end = df_resampled['Timestamp'].iloc[i]
        y1 = avg_momentum.iloc[i-1]
        y2 = avg_momentum.iloc[i]
        
        if y1 > 0.5 and y2 > 0.5:
            color = 'green'
        elif y1 < -0.5 and y2 < -0.5:
            color = 'red'
        elif -0.5 <= y1 <= 0.5 and -0.5 <= y2 <= 0.5:
            color = 'grey'
        else:
            if y2 > 0.5:
                color = 'green'
            elif y2 < -0.5:
                color = 'red'
            else:
                color = 'grey'
        
        ax.plot([start, end], [y1, y2], color=color)
    
    ax.plot([], [], color='blue', label='Average Total Momentum Scores')
    
    btc_data = df[df['Symbol'] == 'BTCUSDT.P']
    if not btc_data.empty:
        btc_data_resampled = btc_data.set_index('Timestamp').resample('5T').mean().reset_index()
        ax.plot(btc_data_resampled['Timestamp'], btc_data_resampled['Momentum Score'], 
                color='yellow', label='Momentum Score for BTCUSDT.P')
    else:
        logging.warning("No BTC data available for plotting")
    
    ax.axhline(y=0, color='black', linestyle='--')
    
    ax.set_ylim(-2, 2)
    ax.set_xlabel('Timestamp (UTC)')
    ax.set_ylabel('Momentum Score')
    
    # Place legend outside the plot
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    ax.grid(True)
    
    plt.gcf().autofmt_xdate()
    
    # Adjust layout to prevent cutting off the legend
    plt.tight_layout()
    
    return fig

def display_top_20_scores(results, historical_df):
    sorted_results = sorted(results, key=lambda x: x['Momentum Score'], reverse=True)
    
    long_df = pd.DataFrame(sorted_results[:20])
    short_df = pd.DataFrame(sorted_results[-20:][::-1])
    
    for df in [long_df, short_df]:
        if not df.empty:
            df['Previous Score'] = df['Symbol'].map(historical_df.set_index('Symbol')['Momentum Score'].to_dict())
            df['Change'] = df['Momentum Score'] - df['Previous Score'].fillna(0)
            df['Momentum Score'] = df['Momentum Score'].round(2)
            df['Change'] = df['Change'].round(2)
    
    return long_df, short_df

def selective_cache_clear():
    global last_cache_clear
    current_time = datetime.now()
    
    if current_time - last_cache_clear >= timedelta(hours=1):
        cache.clear()
        logging.info("TTLCache cleared")
        
        for caching_function in [fetch_all_data, get_historical_data]:
            caching_function.clear()
        logging.info("Streamlit cache selectively cleared")
        
        last_cache_clear = current_time

def main():
    st.title('Crypto Market Momentum Score Dashboard')
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        plot_placeholder = st.empty()
    
    with col2:
        long_scores_placeholder = st.empty()
        short_scores_placeholder = st.empty()
    
    while True:
        try:
            # Read existing data from PostgreSQL
            df = get_historical_data()
            df['Timestamp'] = df['Timestamp'].dt.tz_localize('UTC')
            historical_df = df[['Symbol', 'Momentum Score']].copy()
            
            results = []
            error_symbols = []
            current_datetime = datetime.now(timezone.utc)
            
            for symbol in symbols:
                data = {}
                for interval, weight in intervals.items():
                    analysis = fetch_all_data(symbol, exchange, screener, interval)
                    data[interval] = analysis
                
                if all(value is None for value in data.values()):
                    error_symbols.append(symbol)
                else:
                    weighted_score = sum(weight * calculate_momentum_score({interval: data[interval]}) for interval, weight in intervals.items() if data[interval] is not None)
                    results.append({"Symbol": symbol, "Momentum Score": weighted_score, "Timestamp": current_datetime})
            
            new_df = pd.DataFrame(results)
            new_df['Average Momentum'] = new_df['Momentum Score'].mean()
            
            # Save the updated DataFrame to PostgreSQL
            new_df.to_sql('momentum_scores', con=engine, if_exists='append', index=False)
            
            # Combine new data with historical data for plotting
            df = pd.concat([df, new_df], ignore_index=True)
            
            # Update plot
            fig = update_plot(df)
            plot_placeholder.pyplot(fig)
            
            # Display top 20 scores
            long_df, short_df = display_top_20_scores(results, historical_df)
            
            # Update the placeholders with the latest data
            with long_scores_placeholder.container():
                st.subheader("Top 20 Long Momentum Scores:")
                st.dataframe(long_df[['Symbol', 'Momentum Score', 'Change']])
                avg_change_long = long_df['Change'].mean()
                st.metric("Average Change in Top 20 Long Scores", f"{avg_change_long:.2f}", f"{avg_change_long:.2f}")
            
            with short_scores_placeholder.container():
                st.subheader("Top 20 Short Momentum Scores:")
                st.dataframe(short_df[['Symbol', 'Momentum Score', 'Change']])
                avg_change_short = short_df['Change'].mean()
                st.metric("Average Change in Top 20 Short Scores", f"{avg_change_short:.2f}", f"{avg_change_short:.2f}")
            
            # Selectively clear cache
            selective_cache_clear()
            
            # Sleep for a certain interval before the next update
            time.sleep(60)  # Adjust as needed
            
        except Exception as e:
            log_error(f"An error occurred: {str(e)}")
            st.error(f"An error occurred. Please check the logs for details.")
            time.sleep(600)  # Wait before retrying

if __name__ == "__main__":
    main()
