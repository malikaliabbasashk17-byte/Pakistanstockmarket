import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta

class Analysis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['analyze'])
    async def psx(self, ctx, symbol: str):
        ticker = f"{symbol.upper()}.KA"
        df = yf.download(ticker, period="1mo", interval="1d", progress=False)
        if df.empty:
            await ctx.send(f"❌ {symbol.upper()} ka data nahi mila.")
            return
        
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        price = df['Close'].iloc[-1]
        await ctx.send(f"📊 **{symbol.upper()}**: Price {price:.2f}, RSI {rsi:.2f}")

    @commands.command()
    async def chart(self, ctx, symbol: str):
        ticker = f"{symbol.upper()}.KA"
        df = yf.download(ticker, period="1mo", interval="1d", progress=False)
        if df.empty: return await ctx.send("❌ Data error.")
        status = "Bullish" if df['Close'].iloc[-1] > df['Open'].iloc[-1] else "Bearish"
        await ctx.send(f"📈 **{symbol.upper()}** status: {status}")

def setup(bot):
    bot.add_cog(Analysis(bot))
