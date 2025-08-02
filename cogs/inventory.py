# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands

from config import GUILD_ID

from data.database import get_user_inventory, get_item

class InventoryView(discord.ui.View):
    def __init__(self, author: discord.User, inventory: list, per_page=3):
        super().__init__(timeout=60)
        self.author = author
        self.inventory = inventory
        self.per_page = per_page
        self.current_page = 0
        self.max_page = (len(inventory) - 1)

    async def update_embed(self, interaction: discord.Interaction):
        start = self.current_page * self.per_page
        end = start + self.per_page
        embed = discord.Embed(title=f"{self.author.display_name}'s Inventory", color=discord.Color.blurple())

        for item in self.inventory[start:end]:
            item_data = get_user_inventory(item["name"])
            description = item_data["description"] if item_data else "No description"
            embed.add_field(name=f"{item['name']} x{item['quantity']}", value=description, inline=False)

        embed.set_footer(text=f"Page {self.current_page + 1}/{self.max_page + 1}")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            return await interaction.response.send_message("You can't control this inventory!", ephemeral=True)
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_embed(interaction)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            return await interaction.response.send_message("You can't control this inventory!", ephemeral=True)
        if self.current_page < self.max_page:
            self.current_page += 1
            await self.update_embed(interaction)

# Class for Inventory Cog.
class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="inventory", description="View your inventory.")
    @app_commands.guilds(GUILD_ID)
    async def inventory(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        inventory = get_user_inventory(guild_id, user_id)

        if not inventory:
            await interaction.response.send_message("Your inventory is empty!", ephemeral=True)
            return

        # Show first page
        view = InventoryView(interaction.user, inventory)
        start = 0
        end = view.per_page
        embed = discord.Embed(title=f"{interaction.user.display_name}'s Inventory", color=discord.Color.blurple())

        for item in inventory[start:end]:
            item_data = get_item(item["name"])
            description = item_data["description"] if item_data else "No description"
            embed.add_field(name=f"{item['name']} x{item['quantity']}", value=description, inline=False)

        embed.set_footer(text=f"Page 1/{view.max_page + 1}")
        await interaction.response.send_message(embed=embed, view=view)

# Adds Cog to Town-Keepers Bot Class.
async def setup(bot):
    await bot.add_cog(Inventory(bot))