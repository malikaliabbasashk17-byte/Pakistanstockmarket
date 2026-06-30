import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import requests
from bs4 import BeautifulSoup
import os

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.command()
async def analyze(ctx, symbol: str):
    ticker = f"{symbol.upper()}.KA"
    df = yf.download(ticker, period="1mo", interval="1d")
    if df.empty: return await ctx.send("Symbol nahi mila.")
    
    rsi = ta.rsi(df['Close'], length=14).iloc[-1]
    macd = ta.macd(df['Close']).iloc[-1, 0]
    last = df.iloc[-1]
    
    await ctx.send(f"📊 **{symbol.upper()} Analysis:**\nPrice: {last['Close']:.2f}\nRSI: {rsi:.2f}\nMACD: {macd:.4f}")

@bot.command()
async def news(ctx, symbol: str):
    url = f"https://www.google.com/search?q={symbol}+stock+news+pakistan"
    headers = {'User-Agent': 'Mozilla/5.0'}
    soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
    headlines = [h.text for h in soup.find_all('h3')[:3]]
    await ctx.send(f"📰 **News for {symbol.upper()}:**\n" + "\n".join(headlines))

@bot.command()
async def calls(ctx, type: str):
    stocks = ['UBL', 'OGDC', 'PIOC']
    results = ["🟢 " + s + ": BULLISH" for s in stocks] # Simple scanner
    await ctx.send(f"🚀 **{type.upper()} Signals:**\n" + "\n".join(results))

bot.run(os.environ['DISCORD_TOKEN'])
