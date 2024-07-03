import streamlit as st
import pandas as pd
from tradingview_ta import TA_Handler, Interval
import io
import numpy as np

# Set the page config
st.set_page_config(
    page_title="Trading Analysis",
    page_icon="🪙",
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

# List of symbols to be analyzed, each appended with ".P"
symbols = [
    "10000LADYSUSDT.P", "10000NFTUSDT.P", "1000BONKUSDT.P", "1000BTTUSDT.P", 
    "1000FLOKIUSDT.P", "1000LUNCUSDT.P", "1000PEPEUSDT.P", "1000XECUSDT.P", 
    "1INCHUSDT.P", "AAVEUSDT.P", "ACHUSDT.P", "ADAUSDT.P", "AGIXUSDT.P", 
    "AGLDUSDT.P", "AKROUSDT.P", "ALGOUSDT.P", "ALICEUSDT.P", "ALPACAUSDT.P", 
    "ALPHAUSDT.P", "AMBUSDT.P", "ANCUSDT.P", "ANKRUSDT.P", "ANTUSDT.P", 
    "APEUSDT.P", "API3USDT.P", "APTUSDT.P", "ARUSDT.P", "ARBUSDT.P", "ARKUSDT.P", 
    "ARKMUSDT.P", "ARPAUSDT.P", "ASTRUSDT.P", "ATAUSDT.P", "ATOMUSDT.P", 
    "AUCTIONUSDT.P", "AUDIOUSDT.P", "AVAXUSDT.P", "AXSUSDT.P", "BADGERUSDT.P", 
    "BAKEUSDT.P", "BALUSDT.P", "BANDUSDT.P", "BATUSDT.P", "BCHUSDT.P", 
    "BELUSDT.P", "BICOUSDT.P", "BIGTIMEUSDT.P", "BITUSDT.P", "BLURUSDT.P", "BLZUSDT.P",
    "BUSDUSDT.P", "C98USDT.P", "CEEKUSDT.P", "CELOUSDT.P", "CELRUSDT.P", "CFXUSDT.P",
    "CHRUSDT.P", "CHZUSDT.P", "CKBUSDT.P", "COCOSUSDT.P", "COMBOUSDT.P", "COMPUSDT.P",
    "COREUSDT.P", "COTIUSDT.P", "CREAMUSDT.P", "CROUSDT.P", "CRVUSDT.P", "CTCUSDT.P",
    "CTKUSDT.P", "CTSIUSDT.P", "CVCUSDT.P", "CVXUSDT.P", "CYBERUSDT.P", "DARUSDT.P",
    "DASHUSDT.P", "DENTUSDT.P", "DGBUSDT.P", "DODOUSDT.P", "DOGEUSDT.P", "DOTUSDT.P",
    "DUSKUSDT.P", "DYDXUSDT.P", "EDUUSDT.P", "EGLDUSDT.P", "ENJUSDT.P", "ENSUSDT.P",
    "EOSUSDT.P", "ETCUSDT.P", "ETHUSDT.P", "ETHWUSDT.P", "FETUSDT.P", "FILUSDT.P",
    "FITFIUSDT.P", "FLOWUSDT.P", "FLRUSDT.P", "FORTHUSDT.P", "FRONTUSDT.P", "FTMUSDT.P",
    "FTTUSDT.P", "FXSUSDT.P", "GALUSDT.P", "GALAUSDT.P", "GFTUSDT.P", "GLMUSDT.P",
    "GLMRUSDT.P", "GMTUSDT.P", "GMXUSDT.P", "GPTUSDT.P", "GRTUSDT.P", "GSTUSDT.P",
    "GTCUSDT.P", "HBARUSDT.P", "HFTUSDT.P", "HIFIUSDT.P", "HIGHUSDT.P", "HNTUSDT.P",
    "HOOKUSDT.P", "HOTUSDT.P", "ICPUSDT.P", "ICXUSDT.P", "IDUSDT.P", "IDEXUSDT.P",
    "ILVUSDT.P", "IMXUSDT.P", "INJUSDT.P", "IOSTUSDT.P", "IOTAUSDT.P", "IOTXUSDT.P",
    "JASMYUSDT.P", "JOEUSDT.P", "JSTUSDT.P", "KASUSDT.P", "KAVAUSDT.P", "KDAUSDT.P",
    "KEYUSDT.P", "KLAYUSDT.P", "KNCUSDT.P", "KSMUSDT.P", "LDOUSDT.P", "LEVERUSDT.P",
    "LINAUSDT.P", "LINKUSDT.P", "LITUSDT.P", "LOOKSUSDT.P", "LOOMUSDT.P", "LPTUSDT.P",
    "LQTYUSDT.P", "LRCUSDT.P", "LTCUSDT.P", "LUNAUSDT.P", "LUNA2USDT.P", "MAGICUSDT.P",
    "MANAUSDT.P", "MASKUSDT.P", "MATICUSDT.P", "MAVUSDT.P", "MCUSDT.P", "MDTUSDT.P",
    "MINAUSDT.P", "MKRUSDT.P", "MNTUSDT.P", "MTLUSDT.P", "MULTIUSDT.P", "NEARUSDT.P",
    "NEOUSDT.P", "NKNUSDT.P", "NMRUSDT.P", "NTRNUSDT.P", "OCEANUSDT.P", "OGUSDT.P",
    "OGNUSDT.P", "OMGUSDT.P", "ONEUSDT.P", "ONTUSDT.P", "OPUSDT.P", "ORBSUSDT.P",
    "ORDIUSDT.P", "OXTUSDT.P", "PAXGUSDT.P", "PENDLEUSDT.P", "PEOPLEUSDT.P", "PERPUSDT.P",
    "PHBUSDT.P", "PROMUSDT.P", "QNTUSDT.P", "QTUMUSDT.P", "RADUSDT.P", "RAYUSDT.P",
    "RDNTUSDT.P", "REEFUSDT.P", "RENUSDT.P", "REQUSDT.P", "RLCUSDT.P", "RNDRUSDT.P",
    "ROSEUSDT.P", "RPLUSDT.P", "RSRUSDT.P", "RSS3USDT.P", "RUNEUSDT.P", "RVNUSDT.P",
    "SANDUSDT.P", "SCUSDT.P", "SCRTUSDT.P", "SEIUSDT.P", "SFPUSDT.P", "SHIB1000USDT.P",
    "SKLUSDT.P", "SLPUSDT.P", "SNXUSDT.P", "SOLUSDT.P", "SPELLUSDT.P", "SRMUSDT.P",
    "SSVUSDT.P", "STGUSDT.P", "STMXUSDT.P", "STORJUSDT.P", "STPTUSDT.P", "STRAXUSDT.P",
    "STXUSDT.P", "SUIUSDT.P", "SUNUSDT.P", "SUSHIUSDT.P", "SWEATUSDT.P", "SXPUSDT.P",
    "TUSDT.P", "THETAUSDT.P", "TLMUSDT.P", "TOMIUSDT.P", "TOMOUSDT.P", "TONUSDT.P",
    "TRBUSDT.P", "TRUUSDT.P", "TRXUSDT.P", "TWTUSDT.P", "UMAUSDT.P", "UNFIUSDT.P",
    "UNIUSDT.P", "USDCUSDT.P", "USTUSDT.P", "VETUSDT.P", "VGXUSDT.P", "VRAUSDT.P",
    "WAVESUSDT.P", "WAXPUSDT.P", "WLDUSDT.P", "WOOUSDT.P", "WSMUSDT.P", "XCNUSDT.P",
    "XEMUSDT.P", "XLMUSDT.P", "XMRUSDT.P", "XNOUSDT.P", "XRPUSDT.P", "XTZUSDT.P",
    "XVGUSDT.P", "XVSUSDT.P", "YFIUSDT.P", "YFIIUSDT.P", "YGGUSDT.P", "ZBCUSDT.P",
    "ZECUSDT.P", "ZENUSDT.P", "ZILUSDT.P", "ZRXUSDT.P"
]

# Define intervals
intervals = [
    Interval.INTERVAL_1_MINUTE,
    Interval.INTERVAL_5_MINUTES,
    Interval.INTERVAL_15_MINUTES,
    Interval.INTERVAL_30_MINUTES,
    Interval.INTERVAL_1_HOUR,
    Interval.INTERVAL_2_HOURS,
    Interval.INTERVAL_4_HOURS,
    Interval.INTERVAL_1_DAY
]

# Fetch data function
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

# Calculate momentum score function
def calculate_momentum_score(data, correlations):
    weights = {'STRONG_BUY': 2, 'BUY': 1, 'NEUTRAL': 0, 'SELL': -1, 'STRONG_SELL': -2}
    score = 0
    for interval, analysis in data.items():
        if analysis:
            rating = analysis.summary['RECOMMENDATION'].upper()
            score += correlations.get(interval, 0) * weights.get(rating, 0)
    return score

# Calculate Pearson correlations dynamically
def calculate_correlations(data):
    # Ensure there are no empty lists and handle cases where data is insufficient
    data = [x for x in data if len(x) > 0]
    if len(data) < 2:
        # Return equal weights if insufficient data for correlation
        return {interval: 1 / len(intervals) for interval in intervals}
    
    try:
        # Create a matrix where rows are different intervals and columns are symbols
        data_matrix = np.array(data).T
        correlation_matrix = np.corrcoef(data_matrix, rowvar=False)
        correlations = {interval: np.mean(correlation_matrix[i]) for i, interval in enumerate(intervals)}
        total_correlation = sum(correlations.values())
        normalized_correlations = {k: v / total_correlation for k, v in correlations.items()}
        return normalized_correlations
    except Exception as e:
        st.error(f"Error in calculating correlations: {e}")
        return {interval: 1 / len(intervals) for interval in intervals}

# Main function
def main():
    st.title('Crypto Momentum Score Analysis')
    
    exchange = "BYBIT"
    screener = "crypto"
    
    if st.button("Calculate Momentum Scores"):
        results = []
        error_symbols = []
        all_data = {interval: [] for interval in intervals}
        
        for symbol in symbols:
            data = {}
            for interval in intervals:
                try:
                    analysis = fetch_all_data(symbol, exchange, screener, interval)
                    if analysis:
                        data[interval] = analysis
                        all_data[interval].append(analysis.summary['RECOMMENDATION'].upper())
                except Exception as e:
                    data[interval] = None
            
            if all(value is None for value in data.values()):
                error_symbols.append(symbol)
            else:
                # Prepare data for correlation calculation
                filtered_data = [list(filter(None, all_data[interval])) for interval in intervals]
                correlations = calculate_correlations(filtered_data)
                momentum_score = calculate_momentum_score(data, correlations)
                results.append({"Symbol": symbol, "Momentum Score": momentum_score})
        
        if results:
            results_df = pd.DataFrame(results)
            results_df.index += 1  # Number the first column in ascending order
            results_df.index.name = 'Index'
            top_20_symbols = results_df.sort_values(by="Momentum Score", ascending=False).head(20)
            
            st.write("Top 20 Symbols for Long Position:")
            st.table(top_20_symbols)

            # Provide the option to download the full results as a CSV file
            csv_buffer = io.StringIO()
            results_df.to_csv(csv_buffer)
            csv_data = csv_buffer.getvalue()
            st.download_button(
                label="Download Momentum Scores as CSV",
                data=csv_data,
                file_name='momentum_scores.csv',
                mime='text/csv'
            )
        else:
            st.write("No data could be fetched for the provided symbols.")

        if error_symbols:
            st.write(f"Could not fetch data for the following symbols: {', '.join(error_symbols)}")

if __name__ == "__main__":
    main()
