import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import os
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Yeh list aap kahin bhi update kar sakte hain
WATCHLIST = ['UBL', 'OGDC', 'PIOC', 'TATM', 'HCAR', 'TREET', 'PSMC', 'LUCK', 'ENGRO', 'DAWH']

@bot.event
async def on_ready():
    print(f'Bot is online: {bot.user}')

@bot.command()
async def psx(ctx, symbol: str):
    try:
        df = yf.download(f"{symbol.upper()}.KA", period="1mo", interval="1d", progress=False)
        if df.empty: return await ctx.send("❌ Ticker error.")
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        await ctx.send(f"📊 **{symbol.upper()}**: Price: {df['Close'].iloc[-1]:.2f} | RSI: {rsi:.2f}")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command()
async def calls(ctx, mode: str):
    status_msg = await ctx.send(f"🔄 Scanning...")
    bullish, bearish = [], []
    for s in WATCHLIST:
        df = yf.download(f"{s}.KA", period="1mo", interval="1d", progress=False)
        if not df.empty:
            rsi = ta.rsi(df['Close'], length=14).iloc[-1]
            if rsi > 50: bullish.append(s)
            else: bearish.append(s)
        await asyncio.sleep(0.1)
    await status_msg.edit(content=f"🚀 **{mode.upper()} Results:**\n🟢 Bullish: {', '.join(bullish)}\n🔴 Bearish: {', '.join(bearish)}")

bot.run(os.environ['DISCORD_TOKEN'])
