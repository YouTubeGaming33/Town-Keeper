# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands

from config import DEVS, GUILD_ID

from data.database import add_item_to_user

# Class for Development Cog.
class Development(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="item", description="Adds Item to Member - Testing Purposes")
    @app_commands.guilds(GUILD_ID)
    async def item(self, interaction: discord.Interaction, member: discord.Member, item: str, quantity: int):
        if interaction.user.id not in DEVS:
            await interaction.response.send_message("You are not a Developer!")
            return
        
        item = item.capitalize()
        success = add_item_to_user(guild_id=interaction.guild.id, user_id=member.id, item_name=item, quantity=quantity)
        if not success:
            await interaction.response.send_message(f"{item} is not a Valid Item in food.json")
        await interaction.response.send_message(f"{quantity} {item} added to {member}")
        

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