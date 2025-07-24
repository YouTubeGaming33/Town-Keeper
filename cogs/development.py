# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands

from config import DEVS, GUILD_ID

# Class for Development Cog.
class Development(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Sends Latency, pong!")
    @app_commands.guilds((GUILD_ID))
    async def ping(self, interaction: discord.Interaction):
        if interaction.user.id not in DEVS:
            await interaction.response.send_message("You are not a Developer!")
            return
        
        latency_ms = round(self.bot.latency * 1000)

        await interaction.response.send_message(f"{latency_ms}ms - Pong!")

# Adds Cog to Town-Keepers Bot Class.
async def setup(bot):
    await bot.add_cog(Development(bot))