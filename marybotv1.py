import streamlit as st
import pandas as pd
from tradingview_ta import TA_Handler, Interval
import io
from datetime import datetime
import os

# Set the page config
st.set_page_config(
    page_title="Análisis de Trading",
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

# List of symbols to be analyzed
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
    "BUSDUSDT.P", "BTCUSDT.P", "C98USDT.P", "CEEKUSDT.P", "CELOUSDT.P", "CELRUSDT.P", "CFXUSDT.P",
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

# Create the 'momentum_data' folder if it doesn't exist
if not os.path.exists('momentum_data'):
    os.makedirs('momentum_data')

# Indicator weights adjusted for better strategy balance
indicator_weights = {
    'RSI': 0.10,            # Relative Strength Index
    'Stoch.K': 0.10,        # Stochastic Oscillator %K
    'Stoch.D': 0.10,        # Stochastic Oscillator %D
    'MACD.macd': 0.15,      # MACD main line
    'MACD.signal': 0.15,    # MACD signal line
    'MACD.histogram': 0.10, # MACD histogram
    'ADX': 0.10,            # Average Directional Index
    'CCI20': 0.10,          # Commodity Channel Index (20-period)
    'ATR': 0.10             # Average True Range
}

def fetch_all_data(symbol, exchange, screener, interval):
    """Fetches trading data for a given symbol and interval from TradingView."""
    handler = TA_Handler(
        symbol=symbol,
        exchange=exchange,
        screener=screener,
        interval=interval,
        timeout=None
    )
    analysis = handler.get_analysis()
    return analysis

def calculate_weighted_indicators(analysis):
    """Calculates weighted values for indicators based on defined weights."""
    weighted_data = {}
    for indicator, weight in indicator_weights.items():
        value = analysis.indicators.get(indicator, 0)  # Default to 0 if indicator data is missing
        weighted_data[indicator] = value * weight
    return weighted_data

def calculate_momentum_score(data):
    """Calculates momentum score based on analysis recommendations."""
    weights = {'STRONG_BUY': 2, 'BUY': 1, 'NEUTRAL': 0, 'SELL': -1, 'STRONG_SELL': -2}
    score = 0
    for interval, analysis in data.items():
        if analysis:
            rating = analysis.summary['RECOMMENDATION'].upper()
            score += weights.get(rating, 0)
    return score

def main():
    st.title('Análisis de Puntuación de Momentum en Criptomonedas')
    
    exchange = st.text_input("Exchange", "BYBIT")
    screener = st.text_input("Screener", "crypto")
    
    # Slider controls for setting interval weights
    intervals = {
        Interval.INTERVAL_1_MINUTE: st.slider("Intervalo 1 Minuto", 0.0, 1.0, 0.1),
        Interval.INTERVAL_5_MINUTES: st.slider("Intervalo 5 Minutos", 0.0, 1.0, 0.1),
        Interval.INTERVAL_15_MINUTES: st.slider("Intervalo 15 Minutos", 0.0, 1.0, 0.2),
        Interval.INTERVAL_30_MINUTES: st.slider("Intervalo 30 Minutos", 0.0, 1.0, 0.1),
        Interval.INTERVAL_1_HOUR: st.slider("Intervalo 1 Hora", 0.0, 1.0, 0.2),
        Interval.INTERVAL_2_HOURS: st.slider("Intervalo 2 Horas", 0.0, 1.0, 0.1),
        Interval.INTERVAL_4_HOURS: st.slider("Intervalo 4 Horas", 0.0, 1.0, 0.1),
        Interval.INTERVAL_1_DAY: st.slider("Intervalo 1 Día", 0.0, 1.0, 0.1)
    }
    
    if st.button("Calcular Puntuaciones de Momentum"):
        results_long = []
        results_short = []
        error_symbols = []
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for symbol in symbols:
            data = {}
            weighted_indicators_data = {}
            for interval, weight in intervals.items():
                try:
                    analysis = fetch_all_data(symbol, exchange, screener, interval)
                    data[interval] = analysis
                    weighted_indicators_data[interval] = calculate_weighted_indicators(analysis)
                except Exception as e:
                    data[interval] = None
                    weighted_indicators_data[interval] = {indicator: None for indicator in indicator_weights}
            
            if all(value is None for value in data.values()):
                error_symbols.append(symbol)
            else:
                weighted_score = sum(weight * calculate_momentum_score({interval: data[interval]}) for interval, weight in intervals.items())
                result = {
                    "Symbol": symbol,
                    "Momentum Score": weighted_score,
                    "Fecha": current_datetime
                }
                for interval in weighted_indicators_data:
                    for indicator, value in weighted_indicators_data[interval].items():
                        result[f'{indicator}_{interval}'] = value
                
                if weighted_score > 0:
                    results_long.append(result)
                else:
                    results_short.append(result)
        
        all_scores = results_long + results_short
        if all_scores:
            avg_momentum_score = sum(item['Momentum Score'] for item in all_scores) / len(all_scores)
            all_results_df = pd.DataFrame(all_scores)
            all_results_df['Promedio Total de Puntuaciones de Momentum'] = avg_momentum_score
            file_name = f"momentum_data/momentum_scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            all_results_df.to_csv(file_name, index=False)
            st.write(f"Datos guardados en {file_name}")
        
            if results_long:
                results_long_df = pd.DataFrame(results_long)
                results_long_df.index += 1  # Numerar la primera columna en orden ascendente
                results_long_df.index.name = 'Índice'
                top_20_long_symbols = results_long_df.sort_values(by="Momentum Score", ascending=False).head(20)
                st.write("Top 20 Símbolos para Posición Larga:")
                st.table(top_20_long_symbols)

            if results_short:
                results_short_df = pd.DataFrame(results_short)
                results_short_df.index += 1  # Numerar la primera columna en orden ascendente
                results_short_df.index.name = 'Índice'
                top_20_short_symbols = results_short_df.sort_values(by="Momentum Score", ascending=True).head(20)
                st.write("Top 20 Símbolos para Posición Corta:")
                st.table(top_20_short_symbols)

            st.write(f"Promedio Total de Puntuaciones de Momentum: {avg_momentum_score:.2f}")

            csv_buffer = io.StringIO()
            all_results_df.to_csv(csv_buffer)
            csv_data = csv_buffer.getvalue()
            st.download_button(
                label="Descargar Puntuaciones de Momentum como CSV",
                data=csv_data,
                file_name='momentum_scores.csv',
                mime='text/csv'
            )
        else:
            st.write("No se pudieron obtener datos para los símbolos proporcionados.")

        if error_symbols:
            st.write(f"No se pudieron obtener datos para los siguientes símbolos: {', '.join(error_symbols)}")

if __name__ == "__main__":
    main()
