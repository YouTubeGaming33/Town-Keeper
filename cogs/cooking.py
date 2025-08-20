# Import Required Discord Libary and Import(s).
import discord
from discord.ext import commands
from discord import app_commands

from data.database import get_user_inventory, remove_item_from_user, add_item_to_user

from discord import SelectOption
from discord.ui import View, Select, Button

def checkInventory(interaction, required_items, required_quantities):
    userInventory = get_user_inventory(interaction.guild.id, interaction.user.id)
    if not userInventory:
        return False

    for item, qty in zip(required_items, required_quantities):
        if userInventory.get(item, 0) < qty:
            return False
    return True

class stewButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Cook", style=discord.ButtonStyle.green)
    async def confirm_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            f"{interaction.user.mention} confirmed the action!",
            ephemeral=True
        )
        
        await interaction.message.edit(view=self)

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "You cancelled Cooking your Masterpiece",
            ephemeral=True
        )
        await interaction.message.delete()


class stewSelect(Select):
    def __init__(self):
        options = [SelectOption(label="Spriggull Stew", description="A Basic Spriggull Stew", emoji="🍲")]

        super().__init__(placeholder="Choose an Option...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Spriggull Stew":
            requiredItems = ["Spriggull Drumstick"]
            requiredQuantite = [4]

            # Check if user has all required items
            if not checkInventory(interaction, requiredItems, requiredQuantite):
                await interaction.response.send_message(
                    "❌ You don't have all the required ingredients!",
                    ephemeral=True
                )
                return

            # Build embed with all ingredients
            ingredients_text = "\n".join(
                f"**{qty}x {item}**" for item, qty in zip(requiredItems, requiredQuantite)
            )
            embed = discord.Embed(
                title="Spriggull Stew Recipe",
                description="Find below the Recipe for your Stew",
                colour=discord.Colour.yellow()
            )
            embed.add_field(name="Ingredients:", value=ingredients_text, inline=False)

            await interaction.response.send_message(embed=embed, view=stewButtons())
        else:
            await interaction.response.send_message("❌ Unknown stew selected.", ephemeral=True)



class stewView(View):
    def __init__(self):
        super().__init__()
        self.add_item(stewSelect())

# Class for Cooking Cog.
class Cooking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="stew", description="Make a stew")
    async def stew(self, interaction: discord.Interaction):
        view = stewView()
        await interaction.response.send_message("Select an Option...", view=view, ephemeral=True)

# Adds Cog to Town-Keepers Bot Class.
async def setup(bot):
    await bot.add_cog(Cooking(bot))