import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import os
import asyncio
import requests
from bs4 import BeautifulSoup

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 100+ Stock Watchlist
WATCHLIST = ['UBL', 'OGDC', 'PIOC', 'TATM', 'HCAR', 'TREET', 'PSMC', 'LUCK', 'ENGRO', 'DAWH', 
             'ATRL', 'CHCC', 'MLCF', 'PIBTL', 'BYCO', 'KAPCO', 'HUBC', 'FFC', 'EFERT', 'PAEL',
             'TRG', 'AVN', 'SYS', 'UNITY', 'HASCOL', 'PSO', 'TELE', 'SNGP', 'SSGC', 'MEBL'] 
# Aap yahan mazeed stock add karte jayen

def get_logic(symbol, mode):
    interval = "15m" if mode == 'intraday' else "1d"
    period = "5d" if mode == 'intraday' else "3mo"
    df = yf.download(f"{symbol}.KA", period=period, interval=interval, progress=False)
    
    if df.empty or len(df) < 14: return None
    
    rsi = ta.rsi(df['Close'], length=14).iloc[-1]
    macd = ta.macd(df['Close'])
    macd_val = macd.iloc[-1, 0]
    macd_sig = macd.iloc[-1, 1]
    
    if rsi > 55 and macd_val > macd_sig: return "BULLISH"
    elif rsi < 45 and macd_val < macd_sig: return "BEARISH"
    return "NEUTRAL"

@bot.command()
async def calls(ctx, mode: str):
    mode = mode.lower()
    if mode not in ['intraday', 'swing']: return await ctx.send("❌ !calls intraday ya !calls swing")
    
    msg = await ctx.send(f"🔄 Scanning {len(WATCHLIST)} stocks for {mode.upper()}...")
    bullish, bearish = [], []
    
    for s in WATCHLIST:
        status = get_logic(s, mode)
        if status == "BULLISH": bullish.append(s)
        elif status == "BEARISH": bearish.append(s)
        await asyncio.sleep(0.05)
    
    res = f"🚀 **{mode.upper()} SCAN:**\n\n🟢 BULLISH: {', '.join(bullish) if bullish else 'Koi nahi'}\n\n🔴 BEARISH: {', '.join(bearish) if bearish else 'Koi nahi'}"
    await msg.edit(content=res)

@bot.command()
async def chart(ctx, symbol: str):
    df = yf.download(f"{symbol.upper()}.KA", period="1mo", interval="1d", progress=False)
    if df.empty: return await ctx.send("❌ Data nahi mila.")
    last = df.iloc[-1]
    status = "Bullish" if last['Close'] > last['Open'] else "Bearish"
    await ctx.send(f"📈 **{symbol.upper()}**: {status} (Close: {last['Close']:.2f})")

@bot.command()
async def news(ctx, symbol: str):
    url = f"https://www.google.com/search?q={symbol}+stock+news+pakistan"
    headers = {'User-Agent': 'Mozilla/5.0'}
    soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
    news_items = [h.text for h in soup.find_all('h3') if len(h.text) > 10][:2]
    await ctx.send(f"📰 **News {symbol.upper()}**: \n" + "\n".join(news_items) if news_items else "Koi news nahi.")

bot.run(os.environ['DISCORD_TOKEN'])
