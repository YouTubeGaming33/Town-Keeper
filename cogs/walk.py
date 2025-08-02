# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands

from config import GUILD_ID

from data.database import add_item_to_user

# Class for Walk Cog.
class Walk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="walk", description="Go for a Walk with your Pet")
    @app_commands.guilds(GUILD_ID)
    async def walk(self, interaction: discord.Interaction):
        return

# Adds Cog to Town-Keepers Bot Class.
async def setup(bot):
    await bot.add_cog(Walk(bot))