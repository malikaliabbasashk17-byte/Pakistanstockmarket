import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Core Watchlist - Top Volume PSX
STOCKS = ['UBL', 'OGDC', 'LUCK', 'ENGRO', 'PIOC', 'UNITY', 'TSML', 'PSO', 'TRG', 'FFC', 'HBL', 'MCB', 'MEBL', 'EPCL', 'AVN']

def get_market_intelligence(symbol):
    try:
        df = yf.download(f"{symbol}.KA", period="100d", interval="1d", progress=False)
        if isinstance(df, tuple): df = df[0]
        if df.empty: return None

        close = df['Close'].squeeze()
        # Indicators
        rsi = ta.rsi(close, length=14).iloc[-1]
        macd = ta.macd(close).iloc[:, 0].iloc[-1]
        bb = ta.bbands(close, length=20)
        
        # Super-Brain Logic: Multi-Layer Scoring
        score = 0
        if rsi < 45: score += 4
        if macd > 0: score += 3
        if close.iloc[-1] > bb.iloc[:, 0].iloc[-1]: score += 3
        
        return {"score": score, "rsi": rsi, "price": close.iloc[-1]}
    except: return None

@bot.command()
async def calls(ctx, mode: str):
    msg = await ctx.send(f"🤖 **Initializing PSX Revolution Engine...**")
    
    results = []
    for s in STOCKS:
        data = get_market_intelligence(s)
        if data and data['score'] >= 7:
            results.append(f"✅ **{s}** | Score: {data['score']}/10 | RSI: {data['rsi']:.1f} | 💰 {data['price']:.2f}")
    
    if results:
        await msg.edit(content=f"🔥 **High Conviction {mode.upper()} Signals:**\n" + "\n".join(results))
    else:
        await msg.edit(content="💤 Market Neutral: No signals meeting high-confidence criteria.")

@bot.command()
async def stats(ctx, symbol: str):
    data = get_market_intelligence(symbol.upper())
    if data:
        await ctx.send(f"📊 **{symbol.upper()} Deep Stats:**\nScore: {data['score']}/10\nRSI: {data['rsi']:.1f}\nPrice: {data['price']:.2f}")
    else:
        await ctx.send("❌ Data unavailable.")

bot.run(os.environ['DISCORD_TOKEN'])
