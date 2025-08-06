# Required Library(s)
import os
import discord

# Pulls Discord Token from .env - If not found then Raises Error.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Variable for GUILD ID - Development Purposes.
GUILD_ID = discord.Object(id=1117429594266533948)

# Variable List for Developers.
DEVS = [581564308689911813, 697528564358184991]

# File Path - Assets.
file_path = "assets"