import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import os

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

@bot.command()
async def analyze(ctx, ticker: str):
    # PSX tickers ke saath .PA lagana parta hai (e.g., OGDC.PA)
    symbol = f"{ticker}.PA"
    data = yf.download(symbol, period="6mo", interval="1d")
    
    if data.empty:
        await ctx.send("Symbol nahi mila. Check karein ke ticker sahi hai (e.g., OGDC).")
        return

    # Indicators calculate karna
    data.ta.rsi(length=14, append=True)
    data.ta.macd(append=True)
    
    last_rsi = data['RSI_14'].iloc[-1]
    
    # Simple Signal Logic
    signal = "NEUTRAL"
    if last_rsi < 30: signal = "BULLISH (Buy Signal)"
    elif last_rsi > 70: signal = "BEARISH (Sell Signal)"
    
    await ctx.send(f"**Analysis for {ticker}:**\n- RSI: {last_rsi:.2f}\n- Signal: {signal}")

bot.run(os.environ['DISCORD_TOKEN'])
