import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import asyncio
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

WATCHLIST = ['UBL', 'OGDC', 'PIOC', 'TATM', 'HCAR', 'PSO', 'PSMC', 'LUCK', 'ENGRO', 'DAWH']

@bot.command(aliases=['analyze'])
async def psx(ctx, symbol: str):
    # .KA suffix check karein
    ticker_symbol = f"{symbol.upper()}.KA"
    df = yf.download(ticker_symbol, period="1mo", interval="1d", progress=False)
    
    # Check if df is a tuple (yfinance version issue) or empty
    if isinstance(df, tuple): df = df[0]
    if df.empty:
        return await ctx.send(f"❌ {symbol.upper()} ka data nahi mila. Shayad ticker ghalat hai.")
    
    rsi = ta.rsi(df['Close'], length=14).iloc[-1]
    await ctx.send(f"📊 **{symbol.upper()}**: Price: {df['Close'].iloc[-1]:.2f} | RSI: {rsi:.2f}")

@bot.command()
async def calls(ctx, mode: str):
    msg = await ctx.send(f"🔄 Scanning {len(WATCHLIST)} stocks...")
    bullish, bearish = [], []
    
    for s in WATCHLIST:
        try:
            df = yf.download(f"{s}.KA", period="1mo", interval="1d", progress=False)
            if isinstance(df, tuple): df = df[0]
            if not df.empty:
                rsi = ta.rsi(df['Close'], length=14).iloc[-1]
                if rsi > 50: bullish.append(s)
                else: bearish.append(s)
        except: continue
        await asyncio.sleep(0.1)
        
    res = f"🚀 **{mode.upper()} Results:**\n🟢 Bullish: {', '.join(bullish) if bullish else 'Koi nahi'}\n🔴 Bearish: {', '.join(bearish) if bearish else 'Koi nahi'}"
    await msg.edit(content=res)

bot.run(os.environ['DISCORD_TOKEN'])
