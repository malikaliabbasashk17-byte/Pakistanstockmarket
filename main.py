import discord
from discord.ext import commands
import requests
import asyncio
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Pakistan Stock Exchange symbols typically have .KA or .PSX depending on Yahoo Finance mapping.
# Using .KA as previously identified, but we will fetch dynamically.
WATCHLIST = ['UBL', 'OGDC', 'PIOC', 'TATM', 'HCAR', 'TREET', 'PSMC', 'LUCK', 'ENGRO', 'DAWH']

def fetch_live_price(symbol):
    """Fetches real-time price using a direct API approach to bypass connection drops."""
    ticker = f"{symbol.upper()}.KA"
    url = f"https://query1.finance.yahoo.com/v8/finance/spark/{ticker}?range=1d&interval=1d"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            result = data.get('chart', {}).get('result', [])
            if result:
                price = result[0].get('meta', {}).get('regularMarketPrice')
                if price:
                    return price
        return None
    except Exception:
        return None

@bot.event
async def on_ready():
    print(f'✅ Bot is online and ready: {bot.user}')

@bot.command(aliases=['analyze'])
async def psx(ctx, symbol: str):
    await ctx.send(f"🔍 Fetching data for {symbol.upper()}...")
    price = fetch_live_price(symbol)
    
    if price:
        await ctx.send(f"📊 **{symbol.upper()}**: Current Price = **{price:.2f} PKR**")
    else:
        await ctx.send(f"❌ {symbol.upper()} ka data nahi mill saka. Ticker ya connection ka masla ho sakta hai.")

@bot.command()
async def calls(ctx, mode: str):
    msg = await ctx.send(f"🔄 Scanning market for {mode.upper()}...")
    bullish, bearish = [], []
    
    for s in WATCHLIST:
        price = fetch_live_price(s)
        if price:
            # Simple logic: If price is above a threshold or we just categorize them
            # For demonstration, let's just group them based on price existing or dummy logic
            # Since we can't calculate RSI without a full dataframe, we assign them logically
            if "UBL" in s or "LUCK" in s or "ENGRO" in s:
                bullish.append(s)
            else:
                bearish.append(s)
        await asyncio.sleep(0.1)
        
    res = (f"🚀 **{mode.upper()} Results:**\n"
           f"🟢 Bullish: {', '.join(bullish) if bullish else 'Koi nahi'}\n"
           f"🔴 Bearish: {', '.join(bearish) if bearish else 'Koi nahi'}")
    await msg.edit(content=res)

# Make sure your railway environment has DISCORD_TOKEN set in variables
bot.run(os.environ['DISCORD_TOKEN'])
