import discord
from discord.ext import commands
import yfinance as yf
import pandas_ta as ta
import requests
from bs4 import BeautifulSoup
import os

# Intents setting
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def calculate_signals_logic(df):
    """Purana final trading logic jo RSI, MACD aur Stochastic ko analyze karta hai"""
    # Technical Indicators Calculations
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # MACD Calculation
    macd_df = ta.macd(df['Close'])
    df['MACD'] = macd_df.iloc[:, 0]
    df['MACD_Signal'] = macd_df.iloc[:, 1]
    
    # Stochastic Calculation
    stoch_df = ta.stoch(df['High'], df['Low'], df['Close'])
    df['Stoch_K'] = stoch_df.iloc[:, 0]
    
    last = df.iloc[-1]
    
    rsi_val = last['RSI']
    macd_val = last['MACD']
    macd_sig = last['MACD_Signal']
    stoch_k = last['Stoch_K']
    
    # Signals scoring matching your original app layout
    bullish_signals = 0
    bearish_signals = 0
    
    if rsi_val > 55: bullish_signals += 1
    elif rsi_val < 45: bearish_signals += 1
    
    if macd_val > macd_sig: bullish_signals += 1
    else: bearish_signals += 1
    
    if stoch_k < 30: bullish_signals += 1
    elif stoch_k > 70: bearish_signals += 1
    
    # Determine Status & Confidence
    total_signals = bullish_signals + bearish_signals
    confidence = (max(bullish_signals, bearish_signals) / 3) * 100 if total_signals > 0 else 33.3
    
    if bullish_signals > bearish_signals:
        signal_text = "🟢 BUY / BULLISH"
        status_simple = "BULLISH"
    elif bearish_signals > bullish_signals:
        signal_text = "🔴 SELL / BEARISH"
        status_simple = "BEARISH"
    else:
        signal_text = "🟡 NEUTRAL / HOLD"
        status_simple = "NEUTRAL"
        
    return {
        'price': last['Close'],
        'rsi': rsi_val,
        'macd': macd_val,
        'macd_sig': macd_sig,
        'stoch_k': stoch_k,
        'signal_text': signal_text,
        'status_simple': status_simple,
        'confidence': confidence
    }

@bot.event
async def on_ready():
    print(f'Pakistan Stock Market Bot ({bot.user}) is now online!')

# --- 1. Original Analysis Command (Supports both !psx and !analyze) ---
@bot.command(aliases=['analyze'])
async def psx(ctx, symbol: str):
    await ctx.send(f"Wait karein, **{symbol.upper()}** ka data analyze ho raha hai...")
    
    ticker = f"{symbol.upper()}.KA"
    df = yf.download(ticker, period="3mo", interval="1d")
    
    if df.empty:
        await ctx.send(f"❌ **{symbol.upper()}** ka data nahi mil saka. Ticker check karein.")
        return
        
    data = calculate_signals_logic(df)
    
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

# --- 2. Dynamic Calls Scanner Command (Intraday & Swing matching the exact indicators) ---
@bot.command()
async def calls(ctx, type: str):
    call_type = type.lower()
    if call_type not in ['intraday', 'swing']:
        await ctx.send("❌ Sahi format use karein: `!calls intraday` ya `!calls swing`")
        return
        
    await ctx.send(f"🚀 Calculating **{call_type.upper()}** signals based on active indicators... Wait karein.")
    
    # Aapke primary trading stocks
    stocks = ['UBL', 'OGDC', 'PIOC']
    results = []
    
    for s in stocks:
        df = yf.download(f"{s}.KA", period="3mo", interval="1d")
        if df.empty: continue
        
        data = calculate_signals_logic(df)
        
        # Intraday vs Swing filter alignment using real calculated data
        if call_type == 'intraday':
            # Intraday picks stocks showing momentum or immediate setups
            emoji = "🟢" if data['status_simple'] == "BULLISH" else ("🔴" if data['status_simple'] == "BEARISH" else "🟡")
            results.append(f"{emoji} {s}: **{data['status_simple']}** (RSI: {data['rsi']:.1f} | Stoch: {data['stoch_k']:.1f}%)")
        else:
            # Swing looks for high confidence trends
            emoji = "🟢" if data['rsi'] > 50 and data['macd'] > data['macd_sig'] else "🔴"
            status = "BULLISH" if emoji == "🟢" else "BEARISH"
            results.append(f"{emoji} {s}: **{status}** (Confidence: {data['confidence']:.1f}%)")
            
    await ctx.send(f"🚀 **{call_type.upper()} Signals List:**\n" + "\n".join(results))

# --- 3. Live News & Announcements Command ---
@bot.command()
async def news(ctx, symbol: str):
    await ctx.send(f"📰 **{symbol.upper()}** ki latest news search ho rahi hai...")
    try:
        url = f"https://www.google.com/search?q={symbol}+stock+news+pakistan"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all('h3')[:3]
        
        if not headlines:
            await ctx.send(f"Jeem, abhi **{symbol.upper()}** ki koi taza announcement nahi mili.")
            return
            
        news_list = "\n".join([f"• {h.text}" for h in headlines])
        await ctx.send(f"📰 **Latest News for {symbol.upper()}:**\n{news_list}")
    except Exception as e:
        await ctx.send("❌ News system temporary down hai. Baqi commands check karein.")

bot.run(os.environ['DISCORD_TOKEN'])
