import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import os

# Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f'✅ Bot active: {bot.user}')

@bot.command(aliases=['psx', 'analyze'])
async def analyze(ctx, symbol: str):
    try:
        ticker_name = f"{symbol.upper()}.KA"
        df = yf.download(ticker_name, period="100d", interval="1d", progress=False)
        
        # DataFrame fix
        if isinstance(df, tuple): df = df[0]
        if df.empty:
            await ctx.send(f"❌ No data found for {symbol.upper()}.")
            return

        close = df['Close'].squeeze()
        high = df['High'].squeeze()
        low = df['Low'].squeeze()
        
        # Indicators
        rsi = ta.rsi(close, length=14).iloc[-1]
        macd = ta.macd(close)
        bb = ta.bbands(close, length=20)
        stoch = ta.stoch(high, low, close)
        
        price = close.iloc[-1]
        
        msg = (f"📈 **Analysis for {symbol.upper()}**\n"
               f"💰 Price: {price:.2f}\n"
               f"🟢 RSI: {rsi:.1f}\n"
               f"📉 MACD: {macd.iloc[:, 0].iloc[-1]:.2f}\n"
               f"⚙️ Stoch: {stoch.iloc[:, 0].iloc[-1]:.1f}\n"
               f"📏 BB Range: {bb.iloc[:, 0].iloc[-1]:.1f} - {bb.iloc[:, 2].iloc[-1]:.1f}")
        
        await ctx.send(msg)
    except Exception as e:
        await ctx.send(f"❌ Error occurred: {str(e)}")

bot.run(os.environ['DISCORD_TOKEN'])
