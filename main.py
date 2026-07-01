import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def get_stock(s):
    # .ka ya bina extension ke dono try karega
    ticker = f"{s.lower()}.ka"
    return yf.Ticker(ticker)

@bot.command()
async def analysis(ctx, s: str):
    await ctx.send(f"⏳ processing report for {s.lower()}...")
    try:
        stock = get_stock(s)
        df = stock.history(period="60d")
        
        # agar .ka se data na mile toh bina extension try karein
        if df.empty:
            stock = yf.Ticker(f"{s.lower()}")
            df = stock.history(period="60d")
            
        if df.empty: raise Exception("data not found")
        
        c = df['close'].iloc[-1] # yfinance column names mostly lowercase hote hain
        rsi = ta.rsi(df['close'], length=14).iloc[-1]
        
        reply = (f"📊 {s.lower()} dashboard\n"
                 f"💰 price: {c:.2f} pkr\n"
                 f"📈 rsi: {rsi:.1f}")
        await ctx.send(reply)
    except Exception as e:
        await ctx.send(f"⚠️ error: data mil nahi raha. ({e})")

@bot.command()
async def market(ctx):
    await ctx.send("⏳ fetching macro data...")
    try:
        # kse100 ke liye symbol '^kse100'
        kse = yf.Ticker("^kse100").history(period="1d")['close'].iloc[-1]
        reply = (f"🌍 macro dashboard\n"
                 f"📈 kse-100: {kse:.2f}\n"
                 f"📰 sentiment: stable")
        await ctx.send(reply)
    except:
        await ctx.send("⚠️ error: macro data nahi mil raha.")

bot.run(os.environ['DISCORD_TOKEN'])
