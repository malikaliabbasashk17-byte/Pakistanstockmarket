import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Helper function to get data safely
def get_full_stock_data(s):
    ticker_str = f"{s.upper()}.KA"
    stock = yf.Ticker(ticker_str)
    df = stock.history(period="60d")
    return stock, df

@bot.command()
async def analysis(ctx, s: str):
    """A-Z Analysis: Technical + Fundamental + Tax + Intraday"""
    msg = await ctx.send(f"⏳ **Fetching complete intel for {s.upper()}...**")
    try:
        stock, df = get_full_stock_data(s)
        c = df['Close'].iloc[-1]
        
        # Technicals
        rsi = ta.rsi(df['Close'], length=14).iloc[-1]
        macd = ta.macd(df['Close']).iloc[:, 0].iloc[-1]
        
        # Fundamentals
        info = stock.info
        pe = info.get('forwardPE', 'N/A')
        mcap = info.get('marketCap', 'N/A')
        
        # Intraday Trend (15m calculation)
        df_15m = stock.history(period="1d", interval="15m")
        trend = "Bullish" if df_15m['Close'].iloc[-1] > df_15m['Open'].iloc[-1] else "Bearish"
        
        reply = (f"📊 **{s.upper()} FULL DASHBOARD**\n"
                 f"---------------------------\n"
                 f"💰 **Price:** {c:.2f} PKR\n"
                 f"📈 **Technical:** RSI: {rsi:.1f} | MACD: {macd:.2f}\n"
                 f"⚡ **Intraday (15m):** {trend} Trend\n"
                 f"🏭 **Fundamentals:** PE: {pe} | M.Cap: {mcap}\n"
                 f"📜 **Tax Info:** CGT 15% (Short term). Consult FBR.")
        await msg.edit(content=reply)
    except:
        await msg.edit(content="❌ Error: Stock data not found. Check symbol.")

@bot.command()
async def market(ctx):
    """Complete Macro View: KSE100 + Oil + Global"""
    msg = await ctx.send(f"⏳ **Scanning Global Macro...**")
    try:
        kse = yf.Ticker("^KSE100").history(period="1d")['Close'].iloc[-1]
        oil = yf.Ticker("BZ=F").history(period="1d")['Close'].iloc[-1]
        
        reply = (f"🌍 **MACRO DASHBOARD**\n"
                 f"---------------------------\n"
                 f"📈 **KSE-100 Index:** {kse:.2f}\n"
                 f"🛢️ **Brent Oil:** ${oil:.2f}\n"
                 f"📰 **Market News:** High volatility in Asian markets impacting local sentiment.\n"
                 f"🔮 **Scenario:** Monitor volume for breakout.")
        await msg.edit(content=reply)
    except:
        await msg.edit(content="❌ Error fetching Macro data.")

@bot.command()
async def helpme(ctx):
    await ctx.send("🤖 **Master Terminal Commands:**\n!analysis [ticker] -> Full A-Z Stock Overview\n!market -> KSE100, Oil & Global Overview")

bot.run(os.environ['DISCORD_TOKEN'])
