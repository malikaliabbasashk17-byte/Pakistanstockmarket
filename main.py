import discord
from discord.ext import commands
import yfinance as yf
import os

# Prefix '!' use kar rahe hain
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Bot active hai: {bot.user}')

# Simple Text Command - Ye kabhi 'CommandNotFound' error nahi degi
@bot.command()
async def psx(ctx, symbol: str):
    await ctx.send(f"Analyzing {symbol.upper()}...")
    try:
        # Data fetch
        ticker = yf.Ticker(f"{symbol.upper()}.KA")
        hist = ticker.history(period="1mo")
        if hist.empty:
            await ctx.send("Data nahi mila, ticker check karein.")
            return
        
        last_price = hist['Close'].iloc[-1]
        await ctx.send(f"Current Price of {symbol.upper()}: {last_price:.2f} PKR")
    except Exception as e:
        await ctx.send(f"Error: {e}")

bot.run(os.environ['DISCORD_TOKEN'])
