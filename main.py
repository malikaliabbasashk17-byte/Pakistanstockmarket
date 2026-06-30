import discord
from discord.ext import commands
import investpy
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def psx(ctx, symbol: str):
    try:
        # Investpy ka PSX data fetcher
        search_result = investpy.search_quotes(text=symbol, products=['stocks'], countries=['pakistan'], n_results=1)
        data = search_result.retrieve_recent_data()
        price = data['Close'].iloc[-1]
        await ctx.send(f"📊 **{symbol.upper()}**: Current Price = **{price} PKR**")
    except Exception as e:
        await ctx.send(f"❌ Data nahi mila. Error: {str(e)}")

bot.run(os.environ['DISCORD_TOKEN'])
