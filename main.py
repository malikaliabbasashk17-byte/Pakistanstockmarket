import discord
from discord.ext import commands
import yfinance as yf
import pandas as pd
import numpy as np
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name='psx')
async def psx_analysis(ctx, symbol: str):
    # Discord command chalne ka message
    await ctx.send(f"Wait karein, {symbol.upper()} ka data analyze ho raha hai...")
    
    # Yahoo Finance ke liye PSX ticker (e.g., UBL.KA or simple symbol check)
    # Pakistan stock symbols usually have .KA or check direct ticker
    ticker_symbol = f"{symbol.upper()}.KA" 
    
    try:
        # 6 mahine ka data daily timeframe par
        df = yf.download(ticker_symbol, period="6mo", interval="1d")
        
        if df.empty or len(df) < 30:
            # Try without suffix if .KA fails
            df = yf.download(symbol.upper(), period="6mo", interval="1d")
            if df.empty:
                await ctx.send(f"❌ {symbol.upper()} ka data nahi mila. Ticker spelling check karein.")
                return

        # Flatten columns if multi-index
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        close_prices = df['Close']

        # 1. RSI Calculation
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]

        # 2. MACD Calculation
        exp1 = close_prices.ewm(span=12, adjust=False).mean()
        exp2 = close_prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=9, adjust=False).mean()
        current_macd = macd.iloc[-1]
        current_signal = signal_line.iloc[-1]

        # 3. Stochastic Oscillator Calculation
        low_14 = close_prices.rolling(window=14).min()
        high_14 = close_prices.rolling(window=14).max()
        stoch_k = 100 * ((close_prices - low_14) / (high_14 - low_14))
        current_stoch_k = stoch_k.iloc[-1]

        # ---- Signal & Confidence Logic ----
        bullish_score = 0
        bearish_score = 0
        
        # RSI Check
        if current_rsi < 30: bullish_score += 2
        elif current_rsi > 70: bearish_score += 2
        
        # MACD Check
        if current_macd > current_signal: bullish_score += 2
        else: bearish_score += 2
        
        # Stochastic Check
        if current_stoch_k < 20: bullish_score += 2
        elif current_stoch_k > 80: bearish_score += 2

        # Final Decision
        confidence = (max(bullish_score, bearish_score) / 6) * 100
        
        if bullish_score > bearish_score:
            action = "🟢 BUY (Bullish)"
        elif bearish_score > bullish_score:
            action = "🔴 SELL (Bearish)"
        else:
            action = "🟡 NEUTRAL (Hold)"

        # Message Formatting
        reply_msg = (
            f"📊 **Stock Analysis for {symbol.upper()}**\n\n"
            f"📈 **Indicators:**\n"
            f"• RSI (14): {current_rsi:.2f}\n"
            f"• MACD: {current_macd:.4f} (Signal: {current_signal:.4f})\n"
            f"• Stochastic K: {current_stoch_k:.2f}%\n\n"
            f"💡 **Signal:** {action}\n"
            f"🎯 **Confidence:** {confidence:.1f}%\n"
        )
        await ctx.send(reply_msg)

    except Exception as e:
        await ctx.send(f"⚠️ Technical Error aa gaya hai: {str(e)[:100]}")

bot.run(os.environ['DISCORD_TOKEN'])
