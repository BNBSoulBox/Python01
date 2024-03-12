import streamlit as st
from tradingview_ta import TA_Handler, Interval
from discord_webhook import DiscordWebhook, DiscordEmbed

# Function to retrieve potential bullish symbols based on analysis results
def select_potential_bullish_symbols(analysis_results):
    bullish_symbols = []
    for symbol_data in analysis_results:
        if is_potential_bullish(symbol_data):
            bullish_symbols.append(symbol_data)
    return bullish_symbols

# Main function
def main():
    # Step 3: Get the user information
    user = db.user.get()
    name = user.name if user and user.name else "you"

    # Step 4: Create the Streamlit interface
    st.sidebar.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-image: linear-gradient(to bottom, #ff0000, #ff00ff);
    }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("Navigation")
    st.sidebar.markdown("💡")
    st.sidebar.markdown("🔍")
    st.sidebar.markdown("📊")

    st.title(f"SOUL BOX TOOL!")

    # Step 5: Get the symbols from the "bnb-pairs-json" library in Databutton
    symbols_json = db.storage.json.get("bnb-pairs-full-json")
    symbols = list(symbols_json.values())

    # List to store symbols with "STRONG_BUY" recommendation
    buy_signals = []

    for symbol in symbols:
        try:
            output = TA_Handler(symbol=symbol,
                                screener='Crypto',
                                exchange='Binance',
                                interval=Interval.INTERVAL_1_HOUR)

            # Step 6: Retrieve the analysis results
            analysis = output.get_analysis()

            # Check if the recommendation is "STRONG_BUY" >= 1 and SELL == 0
            if analysis.summary["RECOMMENDATION"] == "NEUTRAL" and analysis.summary.get("NEUTRAL", 0) >= 11:

                # Check if the symbol meets the defined criteria
                if is_potential_bullish(analysis.indicators):
                    # Store the symbol in the list
                    buy_signals.append(symbol)

        except Exception as e:
            pass  # Ignore errors for now

    # Discord webhook setup
    webhook_url = 'https://discordapp.com/api/webhooks/1138581753620074497/tbiRIAVqsxurA-PXZuKaQODonm6c23VAE-zH_nN4ckawABxMCsUxR2NjJPw3KzlsHy9p'

    # Check if any symbols have a 'STRONG_BUY' recommendation
    if len(buy_signals) == 0:
        st.write("Calma y Paciencia.")
    else:
        st.write("Propsectos:")
        
        # Create a DiscordEmbed object for the response
        embed = DiscordEmbed(title="1H", description="Selección de Fichas 📈:", color=0xFF0000)
        
        # Set author
        embed.set_author(name="XOUL", icon_url="https://cdn.jsdelivr.net/gh/YeiBlock/chatbox@main/assets/img/Xoul%20loGO-1.png")
        
        for symbol in buy_signals:
            st.write(f"Symbol: {symbol}")
            
            # Add a field for each symbol to the DiscordEmbed object
            embed.add_embed_field(name="🌕", value=symbol, inline=False)

        # Set thumbnail
        embed.set_thumbnail(url="https://cdn.jsdelivr.net/gh/YeiBlock/chatbox@main/assets/img/PicsArt_08-10-08.25.46.jpg")
        
        # Set footer
        embed.set_footer(text="MEJORANDO CONTINUAMENTE !!!")

        # Send the Discord message with embedded content
        webhook = DiscordWebhook(url=webhook_url)
        webhook.add_embed(embed)  # Add the embed to the webhook
        response = webhook.execute()

if __name__ == "__main__":
    main()
