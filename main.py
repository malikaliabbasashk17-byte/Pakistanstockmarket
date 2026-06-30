import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

WATCHLIST = ['UBL', 'OGDC', 'PIOC', 'TATM', 'HCAR', 'PSO', 'PSMC', 'LUCK', 'ENGRO', 'DAWH']

# Analysis logic
def get_analysis(symbol):
    df = yf.download(f"{symbol}.KA", period="1mo", interval="1d", progress=False)
    if df.empty: return None
    rsi = ta.rsi(df['Close'], length=14).iloc[-1]
    return {"rsi": rsi, "price": df['Close'].iloc[-1]}

@bot.command()
async def psx(ctx, symbol: str):
    data = get_analysis(symbol.upper())
    if not data: return await ctx.send("Data nahi mila.")
    await ctx.send(f"📊 {symbol.upper()}: Price {data['price']:.2f}, RSI {data['rsi']:.2f}")

@bot.command(aliases=['analyze'])
async def analyze(ctx, symbol: str):
    await psx(ctx, symbol)

@bot.command()
async def calls(ctx, mode: str):
    mode = mode.lower()
    if mode not in ['intraday', 'swing']: return await ctx.send("Sirf 'intraday' ya 'swing' use karein.")
    
    results = []
    for s in WATCHLIST:
        data = get_analysis(s)
        if data and data['rsi'] > 50: results.append(f"{s}: Bullish ({data['rsi']:.1f})")
        elif data and data['rsi'] < 50: results.append(f"{s}: Bearish ({data['rsi']:.1f})")
    
    await ctx.send(f"🚀 {mode.upper()} Results:\n" + "\n".join(results[:10]))

@bot.command()
async def chart(ctx, symbol: str):
    df = yf.download(f"{symbol.upper()}.KA", period="1mo", interval="1d", progress=False)
    status = "Bullish" if df['Close'].iloc[-1] > df['Open'].iloc[-1] else "Bearish"
    await ctx.send(f"📈 {symbol.upper()}: {status}")

bot.run(os.environ['DISCORD_TOKEN'])
