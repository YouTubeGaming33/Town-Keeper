# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands

from discord.ui import Button, View
from discord.app_commands import Choice, choices


from config import GUILD_ID

from data.database import add_item_to_user

class DustBowl(View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Click dis", style=discord.ButtonStyle.grey)
    async def clickdis(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Hallo there")

class Camps(View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Click Me!", style=discord.ButtonStyle.primary)
    async def click_me_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("You clicked the button!", ephemeral=True)

# Class for Walk Cog.
class Walk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="walk", description="Go for a Walk to receive Random Items")
    @app_commands.guilds(GUILD_ID)
    async def walk(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You went on a Walk and Found..!")

    @app_commands.command(name="go-to", description="Go to a Specifc Area")
    @app_commands.guilds(GUILD_ID)
    @app_commands.choices(area=[Choice(name="Camps", value="Camps"), Choice(name="Dust Bowl", value="Dust Bowl"), Choice(name="Forest", value="Forest"), Choice(name="Mines", value="Mines"), Choice(name="Mountain Pass", value="Mountain Pass"), Choice(name="Ponds", value="Ponds"), Choice(name="Tarns", value="Tarns")])
    async def goTo(self, interaction: discord.Interaction, area: Choice[str]):
        area = area.value
        if area == "Camps":
            view=Camps()
            embed = discord.Embed(title="Camps", colour=discord.Colour.green())
        if area == "Dust Bowl":
            view=DustBowl()
            embed = discord.Embed(title="Dust Bowl", colour=discord.Colour.green())
        await interaction.response.send_message(embed=embed,view=view)

# Adds Cog to Town-Keepers Bot Class.
async def setup(bot):
    await bot.add_cog(Walk(bot))