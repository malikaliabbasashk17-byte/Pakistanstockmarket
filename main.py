import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 1. Watchlist (Aap yahan jitne chahain stocks add kar sakte hain)
WATCHLIST = ['UBL', 'OGDC', 'PIOC', 'TATM', 'HCAR', 'TREET', 'PSMC', 'LUCK', 'ENGRO', 'DAWH']

def get_analysis(symbol):
    df = yf.download(f"{symbol}.KA", period="3mo", interval="1d", progress=False)
    if df.empty: return None
    
    # Indicators
    rsi = ta.rsi(df['Close'], length=14).iloc[-1]
    macd = ta.macd(df['Close'])
    macd_val = macd.iloc[-1, 0]
    
    # Pattern Logic
    is_bullish = rsi > 50 and macd_val > 0
    return {"rsi": rsi, "macd": macd_val, "status": "BULLISH" if is_bullish else "BEARISH"}

@bot.command()
async def psx(ctx, symbol: str):
    data = get_analysis(symbol.upper())
    if not data: return await ctx.send("❌ Ticker error. Sahi symbol likhein.")
    await ctx.send(f"📊 **{symbol.upper()} Analysis:** RSI: {data['rsi']:.2f} | Status: {data['status']}")

@bot.command()
async def calls(ctx, trend: str):
    await ctx.send(f"🔍 Scanning Watchlist for {trend.upper()} stocks...")
    results = []
    for s in WATCHLIST:
        data = get_analysis(s)
        if data and data['status'] == trend.upper():
            results.append(f"• {s}: {data['status']}")
    
    if results: await ctx.send(f"🚀 **{trend.upper()} Stocks Found:**\n" + "\n".join(results))
    else: await ctx.send("Koi stock match nahi hua.")

@bot.command()
async def chart(ctx, symbol: str):
    df = yf.download(f"{symbol.upper()}.KA", period="1mo", interval="1d", progress=False)
    if df.empty: return await ctx.send("❌ Data error.")
    
    # Cup & Handle / Momentum Logic
    last_close = df['Close'].iloc[-1]
    avg_close = df['Close'].mean()
    
    if last_close > avg_close * 1.05:
        await ctx.send(f"📈 **{symbol.upper()}**: Bullish Momentum (Breakout possible).")
    else:
        await ctx.send(f"📉 **{symbol.upper()}**: Bearish/Consolidation.")

bot.run(os.environ['DISCORD_TOKEN'])
