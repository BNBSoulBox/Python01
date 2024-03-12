import streamlit as st
import json
from tradingview_ta import TA_Handler, Interval
from discord_webhook import DiscordWebhook, DiscordEmbed

# Function to load symbols from the bnbpairs.json file
def load_symbols_from_json(file_path):
    with open(file_path, 'r') as file:
        symbols = json.load(file)
    return symbols

# Define your potential bullish condition based on the indicators
def is_potential_bullish(indicators):
    # Placeholder function, replace with your actual logic
    return True

def select_potential_bullish_symbols(symbols):
    bullish_symbols = []
    for symbol in symbols:
        try:
            output = TA_Handler(symbol=symbol,
                                screener='Crypto',
                                exchange='Binance',
                                interval=Interval.INTERVAL_1_HOUR)
            analysis = output.get_analysis()
            if analysis.summary["RECOMMENDATION"] == "NEUTRAL" and analysis.summary.get("NEUTRAL", 0) >= 11:
                if is_potential_bullish(analysis.indicators):
                    bullish_symbols.append(symbol)
        except Exception as e:
            st.error(f"Error processing symbol {symbol}: {str(e)}")
    return bullish_symbols

def setup_discord_notification(buy_signals):
    webhook_url = 'https://discordapp.com/api/webhooks/1138581753620074497/tbiRIAVqsxurA-PXZuKaQODonm6c23VAE-zH_nN4ckawABxMCsUxR2NjJPw3KzlsHy9p'
    if buy_signals:
        embed = DiscordEmbed(title="1H", description="Selección de Fichas 📈:", color=0xFF0000)
        embed.set_author(name="XOUL", icon_url="https://cdn.jsdelivr.net/gh/YeiBlock/chatbox@main/assets/img/Xoul%20loGO-1.png")
        
        for symbol in buy_signals:
            embed.add_embed_field(name="🌕", value=symbol, inline=False)

        embed.set_thumbnail(url="https://cdn.jsdelivr.net/gh/YeiBlock/chatbox@main/assets/img/PicsArt_08-10-08.25.46.jpg")
        embed.set_footer(text="MEJORANDO CONTINUAMENTE !!!")
        
        webhook = DiscordWebhook(url=webhook_url)
        webhook.add_embed(embed)
        response = webhook.execute()
        st.success("Notification sent to Discord!")
    else:
        st.write("No buy signals to notify.")

def main():
    st.sidebar.title("Navigation")
    st.sidebar.markdown("💡 - Instructions\n🔍 - Search\n📊 - Analysis")

    st.title("SOUL BOX TOOL!")

    # Load symbols from the bnbpairs.json file
    symbols = load_symbols_from_json('bnbpairs.json')

    buy_signals = select_potential_bullish_symbols(symbols)

    if buy_signals:
        st.write("Prospectos:")
        for symbol in buy_signals:
            st.write(f"Symbol: {symbol}")
        setup_discord_notification(buy_signals)
    else:
        st.write("Calma y Paciencia.")

if __name__ == "__main__":
    main()
