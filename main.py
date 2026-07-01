import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# PSX Top 30 Volume Active Stocks
WATCHLIST = [
    'UBL', 'OGDC', 'LUCK', 'ENGRO', 'PIOC', 'UNITY', 'TSML', 'PSO', 'TRG', 'FFC',
    'HUBC', 'HBL', 'MCB', 'MEBL', 'EPCL', 'AVN', 'TATM', 'TELE', 'PRL', 'DGKC',
    'KOHC', 'MLCF', 'PAEL', 'KEL', 'SNGP', 'SSGC', 'GAS', 'BYCO', 'PPL', 'NBP'
]

def analyze_stock(symbol):
    try:
        # ".KA" format for PSX
        df = yf.download(f"{symbol.upper()}.KA", period="60d", interval="1d", progress=False)
        if isinstance(df, tuple): df = df[0]
        if df.empty: return None
        
        close = df['Close'].squeeze()
        high = df['High'].squeeze()
        low = df['Low'].squeeze()
        
        rsi = ta.rsi(close, length=14).iloc[-1]
        macd = ta.macd(close).iloc[:, 0].iloc[-1]
        stoch = ta.stoch(high, low, close).iloc[:, 0].iloc[-1]
        
        # Scoring System
        score = 0
        if rsi < 40: score += 3
        if macd > 0: score += 3
        if stoch < 30: score += 4
        
        if score >= 6:
            return {"rsi": rsi, "score": score}
        return None
    except: return None

@bot.command()
async def calls(ctx, mode: str):
    await ctx.send(f"🔄 Scanning Top 30 PSX stocks for {mode.upper()}...")
    bullish = []
    
    # Scanning through the list
    for s in WATCHLIST:
        data = analyze_stock(s)
        if data:
            bullish.append(f"🟢 **{s}** | Score: {data['score']}/10 | RSI: {data['rsi']:.1f}")
            
    if bullish:
        await ctx.send(f"🚀 **Strong Bullish Found ({mode.upper()}):**\n" + "\n".join(bullish))
    else:
        await ctx.send("📉 Koi strong bullish stock nahi mila.")

bot.run(os.environ['DISCORD_TOKEN'])
