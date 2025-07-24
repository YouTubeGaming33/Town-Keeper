import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select

from config import GUILD_ID
from data.pet_data import load_pets
from data.database import adopt_pet

class AdoptDropdown(Select):
    def __init__(self, options_data):
        self.pet_map = {opt["Pet"]: opt for opt in options_data}
        options = []
        for opt in options_data:
            options.append(discord.SelectOption(
                label=opt.get("Pet"),
                emoji=opt.get("Emoji")
            ))
        
        super().__init__(placeholder="Choose a Pet...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        chosen_label = self.values[0]
        pet = self.pet_map.get(chosen_label)

        adopt_pet(interaction.user.id, pet)  # Save adoption to DB

        await interaction.response.send_message(f"You adopted: {chosen_label}!", ephemeral=True)



class DropdownView(View):
    def __init__(self, options_data):
        super().__init__()
        self.add_item(AdoptDropdown(options_data))


class Pets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.options_data = load_pets()  # Call the function and store result

    @app_commands.command(name="adopt", description="Adopt your first pet!")
    @app_commands.guilds(GUILD_ID)
    async def adopt(self, interaction: discord.Interaction):
        view = DropdownView(self.options_data)  # Instantiate with options
        await interaction.response.send_message("Select your Pet!", view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Pets(bot))
