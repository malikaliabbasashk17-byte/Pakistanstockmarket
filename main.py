import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import asyncio
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

WATCHLIST = ['UBL', 'OGDC', 'PIOC', 'TATM', 'HCAR', 'TREET', 'PSMC', 'LUCK', 'ENGRO', 'DAWH']

@bot.event
async def on_ready():
    print(f'Bot is online: {bot.user}')

@bot.command(aliases=['analyze'])
async def psx(ctx, symbol: str):
    try:
        # Ticker fix
        ticker = f"{symbol.upper()}.KA"
        df = yf.download(ticker, period="1mo", interval="1d", progress=False)
        
        # Data validation - Error yahan se hat jayega
        if df is None or df.empty:
            return await ctx.send(f"❌ {symbol.upper()} ka data nahi mila.")
        
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        price = df['Close'].iloc[-1]
        
        # Price agar list mein ho toh handle karein
        if isinstance(price, (list,)): price = price[0]
        if isinstance(rsi, (list,)): rsi = rsi[0]
            
        await ctx.send(f"📊 **{symbol.upper()}**: Price: {price:.2f} | RSI: {rsi:.2f}")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command()
async def calls(ctx, mode: str):
    msg = await ctx.send(f"🔄 Scanning...")
    bullish, bearish = [], []
    for s in WATCHLIST:
        try:
            df = yf.download(f"{s}.KA", period="1mo", interval="1d", progress=False)
            if df is not None and not df.empty:
                rsi = ta.rsi(df['Close'], length=14).iloc[-1]
                if isinstance(rsi, (list,)): rsi = rsi[0]
                if rsi > 50: bullish.append(s)
                else: bearish.append(s)
        except: continue
        await asyncio.sleep(0.1)
    await msg.edit(content=f"🚀 **{mode.upper()} Results:**\n🟢 Bullish: {', '.join(bullish)}\n🔴 Bearish: {', '.join(bearish)}")

bot.run(os.environ['DISCORD_TOKEN'])
