import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# IMPORTANT: Extension load karte waqt dot (.) notation use karein
extensions = ['cogs.analysis', 'cogs.trading']

@bot.event
async def on_ready():
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ Loaded {ext}")
        except Exception as e:
            print(f"❌ Error loading {ext}: {e}")
    print(f"Bot is ready as {bot.user}")

bot.run(os.environ['DISCORD_TOKEN'])
