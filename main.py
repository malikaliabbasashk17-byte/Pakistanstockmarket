import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import requests
from bs4 import BeautifulSoup
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- Logic Helper ---
def get_stock_data(symbol):
    ticker = f"{symbol.upper()}.KA"
    df = yf.download(ticker, period="3mo", interval="1d")
    return df

# --- Commands ---

@bot.command(aliases=['analyze'])
async def psx(ctx, symbol: str):
    # !psx intraday/swing handle karein
    if symbol.lower() in ['intraday', 'swing']:
        await calls(ctx, symbol.lower())
        return

    df = get_stock_data(symbol)
    if df.empty: return await ctx.send("Ticker check karein.")
    
    # Indicators
    rsi = ta.rsi(df['Close'], length=14).iloc[-1]
    macd = ta.macd(df['Close']).iloc[-1, 0]
    stoch = ta.stoch(df['High'], df['Low'], df['Close']).iloc[-1, 0]
    
    reply = (f"📊 **Stock Analysis for {symbol.upper()}**\n"
             f"• RSI: {rsi:.2f} | MACD: {macd:.4f}\n"
             f"• Stochastic K: {stoch:.2f}%")
    await ctx.send(reply)

@bot.command()
async def calls(ctx, type: str):
    stocks = ['UBL', 'OGDC', 'PIOC']
    results = []
    for s in stocks:
        df = get_stock_data(s)
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        signal = "BULLISH" if rsi > 50 else "BEARISH"
        results.append(f"• {s}: {signal}")
    await ctx.send(f"🚀 **{type.upper()} Signals:**\n" + "\n".join(results))

@bot.command()
async def news(ctx, symbol: str):
    url = f"https://www.google.com/search?q={symbol}+stock+news+pakistan"
    headers = {'User-Agent': 'Mozilla/5.0'}
    soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
    headlines = [h.text for h in soup.find_all('h3')[:3]]
    await ctx.send(f"📰 **News:**\n" + "\n".join(headlines))

@bot.command()
async def chart(ctx, symbol: str):
    """Nayi Chart Formation Command"""
    df = get_stock_data(symbol)
    last = df.iloc[-1]['Close']
    prev = df.iloc[-2]['Close']
    
    # Simple Pattern Detection
    if last > prev * 1.02:
        pattern = "🟢 Bullish Momentum (Potential Breakout)"
    elif last < prev * 0.98:
        pattern = "🔴 Bearish Pressure"
    else:
        pattern = "🟡 Neutral/Consolidation"
        
    await ctx.send(f"📈 **Chart Formation for {symbol.upper()}:**\n{pattern}")

bot.run(os.environ['DISCORD_TOKEN'])
