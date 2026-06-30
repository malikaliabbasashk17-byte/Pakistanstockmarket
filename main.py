import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import numpy as np
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

def calculate_indicators(symbol):
    try:
        ticker = f"{symbol.upper()}.KA"
        df = yf.download(ticker, period="100d", interval="1d", progress=False)
        if isinstance(df, tuple): df = df[0]
        if df.empty: return None

        close = df['Close'].squeeze()
        high = df['High'].squeeze()
        low = df['Low'].squeeze()
        
        # Indicators
        rsi = ta.rsi(close, length=14).iloc[-1]
        macd = ta.macd(close)
        bb = ta.bbands(close, length=20)
        stoch = ta.stoch(high, low, close)
        sma = ta.sma(close, length=50).iloc[-1]
        
        # Pivot Points
        pivot = (high.iloc[-1] + low.iloc[-1] + close.iloc[-1]) / 3
        
        # Signals
        price = close.iloc[-1]
        trend = "Bullish" if price > sma else "Bearish"
        
        return {
            "price": float(price),
            "rsi": float(rsi),
            "macd": float(macd.iloc[:, 0].iloc[-1]),
            "stoch": float(stoch.iloc[:, 0].iloc[-1]),
            "bb_upper": float(bb.iloc[:, 2].iloc[-1]),
            "bb_lower": float(bb.iloc[:, 0].iloc[-1]),
            "sma": float(sma),
            "pivot": float(pivot),
            "tp": float(price * 1.05),
            "sl": float(price * 0.95),
            "vol": int(df['Volume'].iloc[-1]),
            "trend": trend
        }
    except: return None

@bot.event
async def on_ready():
    print(f'✅ Bot is online: {bot.user}')

@bot.command(aliases=['psx', 'analyze'])
async def analyze(ctx, symbol: str):
    data = calculate_indicators(symbol)
    if data:
        msg = (f"📈 **Technical Report: {symbol.upper()}**\n"
               f"💰 Price: **{data['price']:.2f}** | Trend: {data['trend']}\n"
               f"🟢 RSI: {data['rsi']:.1f} | 📊 SMA(50): {data['sma']:.2f}\n"
               f"⚙️ Stoch: {data['stoch']:.1f} | 📉 MACD: {data['macd']:.2f}\n"
               f"🔮 Pivot: {data['pivot']:.2f}\n"
               f"🎯 Target: {data['tp']:.2f} | 🛑 SL: {data['sl']:.2f}\n"
               f"📏 BB Range: {data['bb_lower']:.1f} - {data['bb_upper']:.1f}")
        await ctx.send(msg)
    else:
        await ctx.send(f"❌ Error: Could not fetch data for {symbol.upper()}.")

bot.run(os.environ['DISCORD_TOKEN'])
