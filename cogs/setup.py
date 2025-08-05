from config import GUILD_ID
import discord
from discord import app_commands
from discord.ext import commands

class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="Town Keeper Set-up Guide:",
                    description="Follow the Instructions below to Set-up Ton Keeper for your Server.",
                    colour=discord.Colour.blue()
                )

            await channel.send(embed=embed)
async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
