import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import os

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# --- Technical Analysis ---
@bot.command()
async def analyze(ctx, symbol: str):
    ticker = f"{symbol.upper()}.KA"
    df = yf.download(ticker, period="1mo", interval="1d")
    if df.empty: return await ctx.send("Data nahi mila.")
    
    rsi = ta.rsi(df['Close'], length=14).iloc[-1]
    macd = ta.macd(df['Close']).iloc[-1, 0]
    last = df.iloc[-1]
    
    await ctx.send(f"📊 **{symbol.upper()} Analysis:**\nPrice: {last['Close']:.2f}\nRSI: {rsi:.2f}\nMACD: {macd:.4f}")

# --- Uniform Signals Command ---
@bot.command()
async def calls(ctx, type: str):
    await ctx.send(f"Calculating {type.upper()} signals...")
    stocks = ['UBL', 'OGDC', 'PIOC']
    results = []
    
    for s in stocks:
        df = yf.download(f"{s}.KA", period="1mo", interval="1d")
        if df.empty: continue
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        
        # Consistent Logic: RSI > 50 for Intraday, RSI > 60 for Swing
        if type == "intraday":
            signal = "BULLISH" if rsi > 50 else "BEARISH"
        else: # Swing
            signal = "BULLISH" if rsi > 60 else "BEARISH"
            
        results.append(f"• {s}: {signal} (RSI: {rsi:.2f})")
    
    await ctx.send(f"🚀 **{type.upper()} Signals:**\n" + "\n".join(results))

bot.run(os.environ['DISCORD_TOKEN'])
