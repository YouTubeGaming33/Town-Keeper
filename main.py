# Required Discord Library(s).
import discord
from discord.ext import commands

# Required OS Library.
import os

# Imports from config.py - Required for Token and GUILD ID.
from config import DISCORD_TOKEN, GUILD_ID

# Sets DISCORD_TOKEN to TOKEN Variable.
TOKEN = DISCORD_TOKEN

# Required Asyncio Library - Organisation. 
import asyncio

# Set Intents to .all - Allows for Use of All Intents without adding additional.
intents = discord.Intents.all()

# Bot Class - Initiates, Loads Cog(s), Syncs Commands.
class TownKeeper(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"Successfully Loaded Cog: {filename}")
            
        try:
            synced = await self.tree.sync(guild=GUILD_ID)
            print(f"Successfully Synced {len(synced)} Command(s)")
            global_synced = await self.tree.sync()
            print (f"Successfully Synced {len(global_synced)} Command(s)")
        except Exception as e:
            print(f"Failed to Sync Commands: {e}")

# Makes TownKeeper() Class Function into a Variable.
bot = TownKeeper()

# Bot Event for when Ready.
@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}")

# Async Function for Starting Bot.
async def main():
    async with bot:
        await bot.start(TOKEN)

# Asyncio Run Command for Main Function.
asyncio.run(main())