import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import numpy as np
import os
# Bot ke top par intents ke neeche ye add karein
bot.remove_command('help') 

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Technical Indicators Calculation Engine
# Technical Indicators Calculation Engine
def calculate_indicators(symbol):
    try:
        ticker = f"{symbol.upper()}.KA"
        df = yf.download(ticker, period="60d", interval="1d", progress=False)
        if isinstance(df, tuple): df = df[0]
        if df.empty: return None

        # Indicators
        close = df['Close'].squeeze()
        rsi = ta.rsi(close, length=14).iloc[-1]
        bb = ta.bbands(close, length=20)
        
        # Signals & Levels
        price = close.iloc[-1]
        bb_upper = bb.iloc[:, 2].iloc[-1]
        bb_lower = bb.iloc[:, 0].iloc[-1]
        
        # Target & Stoploss
        tp = price * 1.05 
        sl = price * 0.95 
        
        return {
            "price": float(price),
            "rsi": float(rsi),
            "bb_upper": float(bb_upper),
            "bb_lower": float(bb_lower),
            "tp": float(tp),
            "sl": float(sl),
            "volume": int(df['Volume'].iloc[-1])
        }
    except Exception as e:
        return None

@bot.command(aliases=['analyze', 'psx_anal'])
async def psx(ctx, symbol: str):
    await ctx.send(f"🔄 Processing live technical data for {symbol.upper()}...")
    data = calculate_indicators(symbol)
    if data:
        response = (f"📈 **Pro Analysis: {symbol.upper()}**\n"
                    f"💰 Price: **{data['price']:.2f}** | Vol: {data['volume']}\n"
                    f"🟢 RSI: {data['rsi']:.1f}\n"
                    f"📊 BB Range: {data['bb_lower']:.1f} - {data['bb_upper']:.1f}\n"
                    f"🎯 Target: {data['tp']:.1f} | 🛑 SL: {data['sl']:.1f}")
        await ctx.send(response)
    else:
        await ctx.send(f"❌ Could not fetch data for {symbol.upper()}.")

        )
        await ctx.send(response)
    else:
        await ctx.send(f"❌ Could not fetch data for {symbol.upper()}. Please check the ticker symbol or wait a moment.")

@bot.command()
async def chart(ctx, symbol: str):
    # Extension of commands without disrupting the flow
    await ctx.send(f"📈 Chart command for {symbol.upper()} is ready.")
@bot.command()
async def calls(ctx, mode: str):
    msg = await ctx.send(f"🔄 Scanning market for {mode.upper()}...")
    bullish, bearish = [], []
    
    # Use loop with thread to prevent freezing
    for s in WATCHLIST:
        # Running calculation in thread to keep bot responsive
        data = await asyncio.to_thread(calculate_indicators, s)
        if data:
            if data['rsi'] > 55:
                bullish.append(f"{s} (RSI: {data['rsi']:.1f})")
            elif data['rsi'] < 45:
                bearish.append(f"{s} (RSI: {data['rsi']:.1f})")
        
    res = (f"🚀 **{mode.upper()} Results:**\n\n"
           f"🟢 **Bullish:**\n{', '.join(bullish) if bullish else 'Koi nahi'}\n\n"
           f"🔴 **Bearish:**\n{', '.join(bearish) if bearish else 'Koi nahi'}")
    await msg.edit(content=res)

    

bot.run(os.environ['DISCORD_TOKEN'])
