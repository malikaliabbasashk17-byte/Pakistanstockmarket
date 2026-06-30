import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import requests
from bs4 import BeautifulSoup
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def calculate_master_logic(df):
    """Aapka original structural core logic jo indicators aur confidence calculate karta hai"""
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    macd_df = ta.macd(df['Close'])
    df['MACD'] = macd_df.iloc[:, 0]
    df['MACD_Signal'] = macd_df.iloc[:, 1]
    
    stoch_df = ta.stoch(df['High'], df['Low'], df['Close'])
    df['Stoch_K'] = stoch_df.iloc[:, 0]
    
    last = df.iloc[-1]
    
    rsi_val = last['RSI']
    macd_val = last['MACD']
    macd_sig = last['MACD_Signal']
    stoch_k = last['Stoch_K']
    
    bullish = 0
    bearish = 0
    
    if rsi_val > 53: bullish += 1
    elif rsi_val < 47: bearish += 1
    
    if macd_val > macd_sig: bullish += 1
    else: bearish += 1
    
    if stoch_k < 30: bullish += 1
    elif stoch_k > 70: bearish += 1
    
    confidence = (max(bullish, bearish) / 3) * 100
    
    if bullish > bearish:
        signal_text = "🟢 BUY / BULLISH"
        status_simple = "BULLISH"
    elif bearish > bullish:
        signal_text = "🔴 SELL / BEARISH"
        status_simple = "BEARISH"
    else:
        signal_text = "🟡 NEUTRAL / HOLD"
        status_simple = "NEUTRAL"
        
    return {
        'rsi': rsi_val, 'macd': macd_val, 'macd_sig': macd_sig, 'stoch_k': stoch_k,
        'signal_text': signal_text, 'status_simple': status_simple, 'confidence': confidence,
        'df': df
    }

@bot.event
async def on_ready():
    print(f'{bot.user} online hai!')

# --- 1. Original Analysis (Maching 135183.jpg Layout) ---
@bot.command(aliases=['analyze'])
async def psx(ctx, symbol: str):
    if symbol.lower() in ['intraday', 'swing']:
        await calls(ctx, symbol.lower())
        return
        
    await ctx.send(f"Wait karein, **{symbol.upper()}** ka data analyze ho raha hai...")
    ticker = f"{symbol.upper()}.KA"
    df = yf.download(ticker, period="3mo", interval="1d")
    
    if df.empty:
        await ctx.send(f"❌ **{symbol.upper()}** ka data nahi mil saka. Sahi ticker type karein.")
        return
        
    data = calculate_master_logic(df)
    
    reply = (
        f"📊 **Stock Analysis for {symbol.upper()}**\n\n"
        f"📈 **Technical Indicators:**\n"
        f"• RSI (14): **{data['rsi']:.2f}**\n"
        f"• MACD: **{data['macd']:.4f}** (Signal Line: **{data['macd_sig']:.4f}**)\n"
        f"• Stochastic K: **{data['stoch_k']:.2f}%**\n\n"
        f"💡 **Trading Signal:** {data['signal_text']}\n"
        f"🎯 **Confidence Level:** {data['confidence']:.1f}%"
    )
    await ctx.send(reply)

# --- 2. Live Fixed Signal Calls ---
@bot.command()
async def calls(ctx, type: str):
    call_type = type.lower()
    if call_type not in ['intraday', 'swing']:
        await ctx.send("❌ Format: `!calls intraday` ya `!calls swing`")
        return
        
    await ctx.send(f"🚀 Calculating **{call_type.upper()}** signals... Wait karein.")
    stocks = ['UBL', 'OGDC', 'PIOC']
    results = []
    
    for s in stocks:
        df = yf.download(f"{s}.KA", period="3mo", interval="1d")
        if df.empty: continue
        data = calculate_master_logic(df)
        
        emoji = "🟢" if data['status_simple'] == "BULLISH" else ("🔴" if data['status_simple'] == "BEARISH" else "🟡")
        results.append(f"{emoji} {s}: **{data['status_simple']}** (Confidence: {data['confidence']:.1f}%)")
        
    await ctx.send(f"🚀 **{call_type.upper()} Signals List:**\n" + "\n".join(results))

# --- 3. Live News Scraper ---
@bot.command()
async def news(ctx, symbol: str):
    await ctx.send(f"📰 **{symbol.upper()}** news search ho rahi hai...")
    try:
        url = f"https://www.google.com/search?q={symbol}+stock+news+pakistan"
        headers = {'User-Agent': 'Mozilla/5.0'}
        soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
        headlines = [h.text for h in soup.find_all('h3')[:3]]
        
        news_list = "\n".join([f"• {h}" for h in headlines]) if headlines else "Koi taze khabar nahi mili."
        await ctx.send(f"📰 **Latest News for {symbol.upper()}:**\n{news_list}")
    except:
        await ctx.send("❌ News system down hai.")

# --- 4. NEW: Advanced Chart Pattern & Formation Command ---
@bot.command()
async def chart(ctx, symbol: str):
    await ctx.send(f"🔍 **{symbol.upper()}** ka chart pattern aur candle structure scan ho raha hai...")
    ticker = f"{symbol.upper()}.KA"
    df = yf.download(ticker, period="6mo", interval="1d") # 6 months to detect larger formations
    
    if df.empty:
        await ctx.send("❌ Chart data nahi mil saka.")
        return
        
    # Standard values for calculations
    close_prices = df['Close'].tolist()
    high_prices = df['High'].tolist()
    low_prices = df['Low'].tolist()
    open_prices = df['Open'].tolist()
    
    last_close = close_prices[-1]
    last_open = open_prices[-1]
    
    # 1. Candlestick Pattern Detection
    candle_pattern = "Normal Candle"
    if last_close > last_open:
        body = last_close - last_open
        upper_shadow = high_prices[-1] - last_close
        lower_shadow = last_open - low_prices[-1]
        if lower_shadow > (2 * body) and upper_shadow < (0.5 * body):
            candle_pattern = "🟢 Bullish Hammer (Strong Reversal Sign)"
        else:
            candle_pattern = "🟢 Bullish Marubozu / White Candle"
    else:
        body = last_open - last_close
        upper_shadow = high_prices[-1] - last_open
        lower_shadow = last_close - low_prices[-1]
        if upper_shadow > (2 * body) and lower_shadow < (0.5 * body):
            candle_pattern = "🔴 Shooting Star / Bearish Inverted Hammer"
        else:
            candle_pattern = "🔴 Bearish Black Candle"

    # 2. Chart Formation Detection (Cup and Handle approximation via rolling highs/lows)
    formation = "No clear multi-month formation yet (Consolidation Mode)"
    max_6m = max(close_prices)
    min_6m = min(close_prices)
    
    # Simple Cup & Handle check: if current price is near 6-month highs after a deep correction round bottom
    if last_close >= (max_6m * 0.90) and close_prices[int(len(close_prices)/2)] < (max_6m * 0.75):
        formation = "☕ Cup and Handle Formation Detected! (Potential Big Bullish Breakout)"
    elif last_close <= (min_6m * 1.10) and close_prices[int(len(close_prices)/2)] > (min_6m * 1.25):
        formation = "⚠️ Inverted Cup and Handle / Double Top Pressure"

    reply = (
        f"📈 **Chart & Formation Scan for {symbol.upper()}**\n\n"
        f"🕯️ **Latest Candle:** {candle_pattern}\n"
        f"📐 **Chart Structure:** {formation}\n"
        f"📍 **Current Price Position:** Current: **{last_close:.2f}** [6M High: {max_6m:.2f} | 6M Low: {min_6m:.2f}]"
    )
    await ctx.send(reply)

bot.run(os.environ['DISCORD_TOKEN'])
