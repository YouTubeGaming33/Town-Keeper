# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands

from discord.ui import Button, View
from discord.app_commands import Choice, choices

import time
import random

from config import GUILD_ID

from data.database import add_item_to_user, set_cooldown_timestamp, get_time_since_last_use, get_random_food_item

def randomnum():
    quantity = random.randint(1,3)
    return quantity

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
    async def walk(self, interaction: discord.Interaction):
        cooldowncount = 21600  # 6 hours

        elapsed = get_time_since_last_use(interaction.guild.id, interaction.user.id, "walk")
        if elapsed is not None and elapsed < cooldowncount:
            remaining = cooldowncount - elapsed
            expire_timestamp = int(time.time()) + remaining

            await interaction.response.send_message(
                f"> 🚶 You can walk again <t:{expire_timestamp}:R>.",
                ephemeral=True
            )
            return

        # Update the cooldown time
        set_cooldown_timestamp(interaction.guild.id, interaction.user.id, "walk")

        random_item = get_random_food_item()
        quantity = randomnum()

        print (random_item, quantity)
        add_item_to_user(interaction.guild.id, interaction.user.id, random_item, quantity)

        await interaction.response.send_message(f"> You found {quantity}x {random_item} on your Walk")

    @app_commands.command(name="go-to", description="Go to a Specifc Area")
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