# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands

from config import GUILD_ID

from data.database import get_user_inventory, get_item, get_distinct_item_count, remove_item_from_user  # Assume use_item() to be added

# Dropdown for using an item
class UseItemSelect(discord.ui.Select):
    def __init__(self, author, inventory_slice):
        self.author = author
        options = [
            discord.SelectOption(label=item["name"], description=f"x{item['quantity']}")
            for item in inventory_slice
        ]
        super().__init__(placeholder="Choose an item to use", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message("That's not your inventory!", ephemeral=True)

        item_name = self.values[0]
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        success = remove_item_from_user(guild_id, user_id, item_name, quantity=1)
        if success:
            used_msg = f"You used **{item_name}**!"
        else:
            used_msg = f"You don't have any **{item_name}** left to use!"

        # Fetch updated inventory
        updated_inventory = get_user_inventory(guild_id, user_id)
        view = InventoryView(interaction.user, updated_inventory)
        start = 0
        end = view.per_page

        try:
            item_count = get_distinct_item_count(guild_id=guild_id, user_id=user_id)
        except Exception:
            item_count = 0

        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Inventory",
            description=f"You have a Total of **{item_count}** Different Item(s)",
            colour=discord.Colour.blurple()
        )

        for item in updated_inventory[start:end]:
            item_data = get_item(item["name"])
            description = item_data.get("description", "No description") if item_data else "No description"
            embed.add_field(name=f"{item['name']} x{item['quantity']}", value=description, inline=False)

        embed.set_footer(text=f"Page 1/{view.max_page + 1}")

            # Send as a new ephemeral message — no editing needed
        await interaction.response.send_message(content=used_msg, embed=embed, view=view, ephemeral=True)

        # You can later call a use_item() function here to affect the DB

# Dropdown view
class UseItemView(discord.ui.View):
    def __init__(self, author, inventory_slice):
        super().__init__(timeout=30)
        self.add_item(UseItemSelect(author, inventory_slice))

# Inventory embed view
class InventoryView(discord.ui.View):
    def __init__(self, author: discord.User, inventory: list, per_page=3):
        super().__init__(timeout=60)
        self.author = author
        self.inventory = inventory
        self.per_page = per_page
        self.current_page = 0
        self.max_page = (len(inventory) - 1) // self.per_page

    async def update_embed(self, interaction: discord.Interaction):
        start = self.current_page * self.per_page
        end = start + self.per_page
        try:
            item_count = get_distinct_item_count(guild_id=interaction.guild.id, user_id=interaction.user.id)
            print(f"Distinct item count: {item_count}")
        except Exception as e:
            print(f"Error in get_distinct_item_count: {e}")
            item_count = 0
        embed = discord.Embed(title=f"{interaction.user.display_name}'s Inventory", description=f"You have a Total of **{item_count}** Different Item(s)", colour=discord.Colour.blurple())

        for item in self.inventory[start:end]:
            item_data = get_item(item["name"])
            description = item_data.get("description", "No description") if item_data else "No description"

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

    @discord.ui.button(label="Use Item", style=discord.ButtonStyle.success)
    async def use(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            return await interaction.response.send_message("You can't use items from someone else's inventory!", ephemeral=True)

        start = self.current_page * self.per_page
        end = start + self.per_page
        inventory_slice = self.inventory[start:end]

        await interaction.response.send_message(
            "Select an item to use:", view=UseItemView(self.author, inventory_slice), ephemeral=True
        )

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
        try:
            item_count = get_distinct_item_count(guild_id=guild_id, user_id=user_id)
            print(f"Distinct item count: {item_count}")
        except Exception as e:
            print(f"Error in get_distinct_item_count: {e}")
            item_count = 0
        embed = discord.Embed(title=f"{interaction.user.display_name}'s Inventory", description=f"You have a Total of **{item_count}** Different Item(s)", colour=discord.Colour.blurple())

        for item in inventory[start:end]:
            item_data = get_item(item["name"])
            description = item_data["description"] if item_data else "No description"
            embed.add_field(name=f"{item['name']} x{item['quantity']}", value=description, inline=False)

        embed.set_footer(text=f"Page 1/{view.max_page + 1}")
        await interaction.response.send_message(embed=embed, view=view)

# Adds Cog to Town-Keepers Bot Class.
async def setup(bot):
    await bot.add_cog(Inventory(bot))
