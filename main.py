import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

def get_psx_price(symbol):
    # PSX ki official ya reliable source se scraping
    url = f"https://dps.psx.com.pk/symbol/{symbol.upper()}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Price selector (PSX website structure ke mutabiq)
        price = soup.find('div', {'class': 'symbol_quote_last'}).text.strip()
        return price
    except:
        return None

@bot.command()
async def psx(ctx, symbol: str):
    price = get_psx_price(symbol)
    if price:
        await ctx.send(f"📊 **{symbol.upper()}**: Current Price = **{price} PKR**")
    else:
        await ctx.send(f"❌ {symbol.upper()} ka data fetch nahi ho saka. Symbol check karein.")

bot.run(os.environ['DISCORD_TOKEN'])
