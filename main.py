import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import os

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.command()
async def analyze(ctx, symbol: str):
    # Live approximation: period '5d' aur interval '15m' se data fast milta hai
    ticker = f"{symbol.upper()}.KA"
    df = yf.download(ticker, period="5d", interval="15m")
    
    if df.empty:
        await ctx.send("❌ Data fetch nahi ho raha, ticker check karein.")
        return

    # Pivot Point Calculation (The exact formula used by pro apps)
    last = df.iloc[-1]
    high = df['High'].max()
    low = df['Low'].min()
    close = last['Close']
    
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    
    # Technicals
    rsi = ta.rsi(df['Close'], length=14).iloc[-1]
    macd = ta.macd(df['Close'])
    macd_val = macd.iloc[-1, 0] # MACD Line
    
    reply = (
        f"🔴 **LIVE ANALYSIS: {symbol.upper()}**\n"
        f"💰 **Price:** {close:.2f}\n\n"
        f"📍 **Pivot Points:**\n"
        f"• R1: {r1:.2f} | **PP: {pivot:.2f}** | S1: {s1:.2f}\n\n"
        f"📊 **Indicators:**\n"
        f"• RSI: {rsi:.2f}\n"
        f"• MACD: {macd_val:.4f}\n\n"
        f"💡 **Status:** {'Bullish' if close > pivot else 'Bearish'}"
    )
    await ctx.send(reply)

bot.run(os.environ['DISCORD_TOKEN'])
