import discord
from discord import app_commands
from discord.ext import commands

import time, random

from data.database import add_item_to_user, set_cooldown_timestamp, get_time_since_last_use, get_random_food_item

def randomnum():
    quantity = random.randint(1,3)
    return quantity

class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="daily-loot-crate", description="Receive a Daily Loot Crate")
    async def dailyLootCrate(self, interaction: discord.Interaction):
        cooldowncount = 86400  # 24 hours

        elapsed = get_time_since_last_use(interaction.guild.id, interaction.user.id, "daily")
        if elapsed is not None and elapsed < cooldowncount:
            remaining = cooldowncount - elapsed
            expire_timestamp = int(time.time()) + remaining

            await interaction.response.send_message(
                f"> 🎁 You can receive a daily loot crate <t:{expire_timestamp}:R>.",
                ephemeral=True
            )
            return

        items = []
        while len(items) < 3:
            item = get_random_food_item()
            if item not in items:
                items.append(item)

        quantity1 = randomnum()
        quantity2 = randomnum()
        quantity3 = randomnum()
        quantities = [quantity1, quantity2, quantity3]

        guild = interaction.guild.id
        user = interaction.user.id

        for item, quantity in zip(items, quantities):
            add_item_to_user(guild, user, item, quantity)

        print(items, quantities)

        set_cooldown_timestamp(guild, user, "daily")

        await interaction.response.send_message(
            f"You received your daily loot crate with: " +
            ", ".join(f"{q}x {i}" for i, q in zip(items, quantities)),
            ephemeral=True
        )
async def setup(bot: commands.Bot):
    await bot.add_cog(Misc(bot))