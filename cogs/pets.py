import discord
from discord import app_commands
from discord.ext import commands
import json
import re

from data.database import adopt_pet, get_pet, remove_pet, set_pet_nickname, set_happiness

# Dropdown menu for selecting a pet to adopt
class PetDropdown(discord.ui.Select):
    def __init__(self, pets):
        self.pets = pets
        options = []

        # Pattern to extract custom emoji format like <:name:id>
        emoji_pattern = re.compile(r"<:(\w+):(\d{17,20})>")

        for pet in pets:
            name = pet["Pet"]
            emote_str = pet["assets"].get("emote", "").strip()

            emoji = None
            match = emoji_pattern.fullmatch(emote_str)
            if match:
                try:
                    emoji = discord.PartialEmoji(name=match.group(1), id=int(match.group(2)))
                except:
                    pass

            try:
                option = discord.SelectOption(label=name, emoji=emoji)
                options.append(option)
            except:
                options.append(discord.SelectOption(label=name))

        super().__init__(placeholder="Choose your pet...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        try:
            selected_pet_name = self.values[0]
            pet_info = next((p for p in self.pets if p["Pet"] == selected_pet_name), None)

            if not pet_info:
                await interaction.response.send_message("That pet could not be found.", ephemeral=True)
                return

            # Save to MongoDB
            adopt_pet(interaction.user.id, interaction.guild.id, pet_info)

            emote = pet_info["assets"].get("emote", "")
            icon_url = pet_info["assets"].get("icon", "")

            # Send embed confirmation of adoption
            embed = discord.Embed(
                title=f"{selected_pet_name}!",
                description=f"Congratulations! View your {selected_pet_name} using `/view`!",
                color=discord.Color.dark_grey()
            )
            if icon_url:
                embed.set_thumbnail(url=icon_url)
            embed.set_footer(text="✨ Use /walk to grab things needed for your pet!")
            await interaction.response.send_message(f"> You decided to adopt {selected_pet_name} | {emote}", embed=embed)

        except Exception as e:
            print(f"Error in PetDropdown callback: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("Something went wrong while processing your selection.", ephemeral=True)

# View that contains the dropdown
class PetView(discord.ui.View):
    def __init__(self, pets):
        super().__init__()
        self.add_item(PetDropdown(pets))

# Cog to register commands
class Pets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="adopt", description="Adopt your first pet")
    async def adopt(self, interaction: discord.Interaction):
        # Check if user already has a pet
        if get_pet(guild_id=interaction.guild.id, user_id=interaction.user.id):
            await interaction.response.send_message("You already have a pet!", ephemeral=True)
            return

        # Load pets from JSON
        with open('data/pet.json', 'r', encoding='utf-8') as f:
            pets = json.load(f)

        if not pets:
            await interaction.response.send_message("No pets available right now.", ephemeral=True)
            return

        # Send the dropdown view
        await interaction.response.send_message("Select your First Pet:", view=PetView(pets))

    @app_commands.command(name="set-nickname", description="Update Nickname of your Pet")
    async def set_nickname(self, interaction: discord.Interaction, nickname: str):
        # Very basic inappropriate word filter
        banned_words = [
            "fuck", "shit", "bitch", "asshole", "bastard", "dick", "piss", "damn",
            "cunt", "fag", "nigger", "nigga", "whore", "slut", "douche", "retard",
            "suck", "crap", "bollocks", "bugger", "bloody", "twat", "wank", "jerk",
        ]

        if any(bad_word in nickname.lower() for bad_word in banned_words):
            await interaction.response.send_message(
                "That nickname contains inappropriate words. Try something else.",
                ephemeral=True
            )
            return

        # Check if user has a pet
        petData = get_pet(guild_id=interaction.guild.id, user_id=interaction.user.id)
        if not petData:
            await interaction.response.send_message("You do not have a pet.", ephemeral=True)
            return

        # Update nickname in database
        set_pet_nickname(guild_id=interaction.guild.id, user_id=interaction.user.id, nickname=nickname)
        await interaction.response.send_message(f"Updated Pets Nickname to: {nickname}", ephemeral=True)

    @app_commands.command(name="stats", description="Shows your Pets Stats")
    async def stats(self, interaction: discord.Interaction):
        statData = get_pet(interaction.guild.id, interaction.user.id)

        pet_name = statData.get("pet_name", "Unknown")
        health = statData.get("health", "ded")
        hunger = statData.get("hunger", "ded")

        # Display stats in embed
        embed = discord.Embed(title=f"{interaction.user.display_name}'s {pet_name} Stats:", colour=discord.Colour.yellow())
        embed.add_field(name="Health:", value=health, inline=True)
        embed.add_field(name="Hunger", value=hunger, inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="view", description="View your Pet")
    async def view(self, interaction: discord.Interaction):
        petData = get_pet(guild_id=interaction.guild.id, user_id=interaction.user.id)

        if not petData:
            await interaction.response.send_message("You haven't adopted a Pet", ephemeral=True)
            return

        emote = petData.get("pet_emote", "")
        icon = petData.get("pet_icon", "")
        nickname = petData.get("pet_nickname", "Unknown")
        pet_name = petData.get("pet_name", "Unknown")

        # Create embed with pet details
        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s {pet_name} {emote}",
            colour=discord.Colour.green()
        )
        embed.add_field(name="Type:", value=pet_name, inline=False)
        embed.add_field(name="Nickname:", value=nickname, inline=False)
        embed.set_thumbnail(url=icon)
        embed.set_footer(text="👋 Pet your pet using /pet")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pet", description="Show love to your Pet")
    async def pet(self, interaction: discord.Interaction):
        petData = get_pet(interaction.guild.id, interaction.user.id)
        if not petData:
            await interaction.response.send_message("You have no Pets", ephemeral=True)
            return
        
        print("Here")
        happiness = petData["happiness"]
        maxhappiness = "😄😄😄😄😄"
        print("Here1")
        if happiness == maxhappiness:
            await interaction.response.send_message("You're pet is at Max Happiness!", ephemeral=True)
        
        happiness += "😄"

        set_happiness(interaction.user.id, interaction.guild.id, happiness)

        await interaction.response.send_message(f"Your Pets Happiness is now: {happiness}")

    @app_commands.command(name="abandon", description="Abandon your Pet..")
    async def abandon(self, interaction: discord.Interaction):
        petData = get_pet(guild_id=interaction.guild.id, user_id=interaction.user.id)
        if not petData:
            await interaction.response.send_message("You have no Pets", ephemeral=True)
            return

        # Remove from DB
        remove_pet(guild_id=interaction.guild.id, user_id=interaction.user.id)
        await interaction.response.send_message("You abandoned your Pet...", ephemeral=True)

# Setup
async def setup(bot: commands.Bot):
    await bot.add_cog(Pets(bot))
