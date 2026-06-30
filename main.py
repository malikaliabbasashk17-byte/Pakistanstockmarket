import discord
from discord.ext import commands
import json

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Command load karne ka function
def load_commands():
    with open('commands.json', 'r') as f:
        return json.load(f)

@bot.event
async def on_ready():
    print("Bot is ready and dynamic commands are loaded!")

# Dynamic command handler
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    if message.content.startswith('!'):
        cmd = message.content.split(' ')[0][1:]
        data = load_commands()
        
        if cmd in data:
            await message.channel.send(f"Command '{cmd}' is active: {data[cmd]}")
            # Yahan apni actual logic call karein
    
    await bot.process_commands(message)

bot.run('YOUR_TOKEN')
