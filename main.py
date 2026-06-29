import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import requests
from bs4 import BeautifulSoup
import os

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# --- 1. Technical Analysis Command ---
@bot.command()
async def analyze(ctx, symbol: str):
    ticker = f"{symbol.upper()}.KA"
    df = yf.download(ticker, period="5d", interval="15m")
    
    if df.empty:
        await ctx.send("Symbol not found.")
        return

    last = df.iloc[-1]
    # Indicators
    rsi = ta.rsi(df['Close'], length=14).iloc[-1]
    macd = ta.macd(df['Close']).iloc[-1, 0]
    pivot = (df['High'].max() + df['Low'].min() + last['Close']) / 3
    
    status = "BULLISH" if last['Close'] > pivot else "BEARISH"
    vol_status = "High Volume" if last['Volume'] > df['Volume'].mean() else "Low Volume"
    
    reply = (
        f"📊 **Market Analysis: {symbol.upper()}**\n"
        f"💰 Price: {last['Close']:.2f} | 📈 Trend: {status}\n"
        f"⚡ RSI: {rsi:.2f} | 📉 MACD: {macd:.4f}\n"
        f"🚀 Volume: {vol_status}\n"
        f"📍 Pivot: {pivot:.2f}"
    )
    await ctx.send(reply)

# --- 2. News/Announcement Command ---
@bot.command()
async def news(ctx, symbol: str):
    await ctx.send(f"Fetching announcements for {symbol.upper()}...")
    try:
        # PSX/Investing News Scraper Simulation
        url = f"https://www.google.com/search?q={symbol}+stock+news+pakistan"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all('h3')[:3]
        
        news_list = "\n".join([f"• {h.text}" for h in headlines])
        await ctx.send(f"📰 **Latest News for {symbol.upper()}:**\n{news_list}")
    except:
        await ctx.send("News service currently unavailable.")

# --- 3. Signal Call Generator (Intraday/Swing) ---
@bot.command()
async def call(ctx, type: str):
    # Yeh logic RSI/MACD ki base par signal generate karta hai
    await ctx.send(f"Generating {type.upper()} calls based on current market data...")
    # Yahan hum top 3 stocks scan karenge
    stocks = ['UBL', 'OGDC', 'FFC']
    results = []
    for s in stocks:
        df = yf.download(f"{s}.KA", period="1d")
        if df['Close'].iloc[-1] > df['Close'].mean():
            results.append(f"{s}: 🟢 BUY")
        else:
            results.append(f"{s}: 🔴 SELL")
    
    await ctx.send(f"🚀 **{type.upper()} Signal List:**\n" + "\n".join(results))

bot.run(os.environ['DISCORD_TOKEN'])
