import os
import json
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
    user = get_user_info()
    name = user.name if user and user.name else "you"

    # Step 4: Get the symbols from the "bnb-pairs-json" library
    symbols_json = get_symbols_json()
    symbols = list(symbols_json.values())

    # List to store symbols with "STRONG_BUY" recommendation
    buy_signals = []

    for symbol in symbols:
        try:
            output = TA_Handler(symbol=symbol,
                                screener='Crypto',
                                exchange='Binance',
                                interval=Interval.INTERVAL_4_HOURS)

            # Step 6: Retrieve the analysis results
            analysis = output.get_analysis()

            # Check if the recommendation is "STRONG_BUY" >= 1 and SELL == 0
            if analysis.summary["RECOMMENDATION"] == "NEUTRAL" and analysis.summary.get("NEUTRAL", 0) >= 12:

                # Check if the symbol meets the defined criteria
                if is_potential_bullish(analysis.indicators):
                    # Store the symbol in the list
                    buy_signals.append(symbol)

        except Exception as e:
            pass  # Ignore errors for now

    # Discord webhook setup
    webhook_url = os.environ.get("https://discordapp.com/api/webhooks/1138581753620074497/tbiRIAVqsxurA-PXZuKaQODonm6c23VAE-zH_nN4ckawABxMCsUxR2NjJPw3KzlsHy9p")

    # Check if any symbols have a 'STRONG_BUY' recommendation
    if len(buy_signals) == 0:
        print("Calm & Patience")
    else:
        print("Prospects:")

        # Create a DiscordEmbed object for the response
        embed = DiscordEmbed(title="H", description="Grid Token Picker 📈:", color=0xFF0000)

        # Set author
        embed.set_author(name="XOUL", icon_url="https://cdn.jsdelivr.net/gh/YeiBlock/chatbox@main/assets/img/Xoul%20loGO-1.png")

        for symbol in buy_signals:
            print(f"Symbol: {symbol}")

            # Add a field for each symbol to the DiscordEmbed object
            embed.add_embed_field(name="🌕", value=symbol, inline=False)

        # Set thumbnail
        embed.set_thumbnail(url="https://cdn.jsdelivr.net/gh/YeiBlock/chatbox@main/assets/img/PicsArt_08-10-08.25.46.jpg")

        # Set footer
        embed.set_footer(text="Scalable Improvement !!!")

        # Send the Discord message with embedded content
        webhook = DiscordWebhook(url=webhook_url)
        webhook.add_embed(embed)  # Add the embed to the webhook
        response = webhook.execute()

if __name__ == "__main__":
    main()
