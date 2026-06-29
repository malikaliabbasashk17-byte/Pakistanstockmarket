import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import os

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.command()
async def analyze(ctx, symbol: str):
    await ctx.send(f"Analysing {symbol.upper()} with deep indicators...")
    
    # Data fetch
    df = yf.download(f"{symbol.upper()}.KA", period="1y", interval="1d")
    
    if df.empty:
        await ctx.send("Symbol not found.")
        return

    # Indicators Calculation
    df.ta.rsi(length=14, append=True)
    df.ta.macd(append=True)
    df.ta.bbands(length=20, append=True)
    df.ta.sma(length=50, append=True)
    
    last = df.iloc[-1]
    
    # Volume Analysis
    vol_avg = df['Volume'].rolling(window=20).mean().iloc[-1]
    vol_status = "High Volume" if last['Volume'] > vol_avg else "Low Volume"
    
    # Breakout Logic
    breakout = "BULLISH BREAKOUT" if last['Close'] > last['BBU_20_2.0'] else "Consolidation"
    
    reply = (
        f"📊 **Deep Market Analysis: {symbol.upper()}**\n"
        f"💰 **Price:** {last['Close']:.2f} PKR\n"
        f"📈 **Volume Status:** {vol_status}\n"
        f"🚀 **Breakout Status:** {breakout}\n"
        f"⚡ **RSI:** {last['RSI_14']:.2f} | **MACD:** {last['MACD_12_26_9']:.2f}\n"
        f"⛓️ **Bollinger Upper Band:** {last['BBU_20_2.0']:.2f}\n"
        f"💡 **Candle Status:** {'Bullish' if last['Close'] > last['Open'] else 'Bearish'}"
    )
    await ctx.send(reply)

bot.run(os.environ['DISCORD_TOKEN'])
