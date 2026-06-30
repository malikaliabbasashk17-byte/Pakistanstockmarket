import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import asyncio

class Trading(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.watchlist = ['UBL', 'OGDC', 'PIOC', 'TATM', 'HCAR', 'TREET']

    @commands.command()
    async def calls(self, ctx, mode: str):
        mode = mode.lower()
        if mode not in ['intraday', 'swing']:
            return await ctx.send("❌ !calls intraday ya !calls swing")
        
        await ctx.send(f"🔄 Scanning for {mode.upper()}...")
        results = []
        for s in self.watchlist:
            df = yf.download(f"{s}.KA", period="1mo", interval="1d", progress=False)
            if not df.empty:
                rsi = ta.rsi(df['Close'], length=14).iloc[-1]
                status = "Bullish" if rsi > 50 else "Bearish"
                results.append(f"• {s}: {status}")
            await asyncio.sleep(0.1)
        
        await ctx.send(f"🚀 **{mode.upper()} Results:**\n" + "\n".join(results))

def setup(bot):
    bot.add_cog(Trading(bot))
