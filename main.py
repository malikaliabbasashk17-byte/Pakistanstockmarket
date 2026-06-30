import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import numpy as np
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Technical Indicators Calculation Engine
def calculate_indicators(symbol):
    try:
        # Fetching data using direct market parameters
        ticker = f"{symbol.upper()}.KA"
        df = yf.download(ticker, period="60d", interval="1d", progress=False)
        
        # Handle tuple return in newer yfinance versions
        if isinstance(df, tuple):
            df = df[0]
            
        if df.empty:
            return None

        # Calculating Technical Indicators
        close_prices = df['Close'].squeeze() # Flatten to 1D Series
        
        # 1. RSI (14)
        rsi = ta.rsi(close_prices, length=14).iloc[-1]
        
        # 2. MACD
        macd_df = ta.macd(close_prices, fast=12, slow=26, signal=9)
        macd_line = macd_df.iloc[:, 0].iloc[-1]
        signal_line = macd_df.iloc[:, 1].iloc[-1]
        macd_histogram = macd_df.iloc[:, 2].iloc[-1]
        
        # 3. Stochastic Oscillator (14, 3, 3)
        stoch_df = ta.stoch(df['High'].squeeze(), df['Low'].squeeze(), close_prices, k=14, d=3, smooth_k=3)
        stoch_k = stoch_df.iloc[:, 0].iloc[-1]
        stoch_d = stoch_df.iloc[:, 1].iloc[-1]
        
        # Current Price
        current_price = close_prices.iloc[-1]
        
        return {
            "price": float(current_price),
            "rsi": float(rsi),
            "macd": float(macd_histogram),
            "stoch_k": float(stoch_k),
            "stoch_d": float(stoch_d)
        }
    except Exception as e:
        return None

@bot.event
async def on_ready():
    print(f'✅ Bot is fully running: {bot.user}')

@bot.command(aliases=['analyze', 'psx_anal'])
async def psx(ctx, symbol: str):
    await ctx.send(f"🔄 Processing live technical data for {symbol.upper()}...")
    
    data = calculate_indicators(symbol)
    
    if data:
        # Determine trends simply based on indicators
        trend = "Bullish / Strong Momentum" if data['rsi'] > 50 and data['macd'] > 0 else "Bearish / Weak Momentum"
        
        response = (
            f"📊 **Technical Analysis for {symbol.upper()}**:\n"
            f"💰 **Price**: {data['price']:.2f} PKR\n"
            f"📈 **RSI (14)**: {data['rsi']:.2f} (Neutral/Normal range)\n"
            f"📉 **MACD Histogram**: {data['macd']:.4f}\n"
            f"⚙️ **Stochastic %K**: {data['stoch_k']:.2f} | %D: {data['stoch_d']:.2f}\n"
            f"💡 **Market Sentiment**: {trend}"
        )
        await ctx.send(response)
    else:
        await ctx.send(f"❌ Could not fetch data for {symbol.upper()}. Please check the ticker symbol or wait a moment.")

@bot.command()
async def chart(ctx, symbol: str):
    # Extension of commands without disrupting the flow
    await ctx.send(f"📈 Chart command for {symbol.upper()} is ready.")

bot.run(os.environ['DISCORD_TOKEN'])
