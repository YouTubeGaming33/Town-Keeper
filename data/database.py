# Required Library(s) and Import(s)
import os

from datetime import datetime

from pymongo import MongoClient

# Pulls MONGO=DB URI from .env - If not found then Raises ValueError.
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("No MongoDB URI found in environment variables")

# Setting up Database, Client and Collections.
client = MongoClient(MONGO_URI)
db = client["townkeeper"]
adoptions = db["adoptions"]

def adopt_pet(user_id: int, guild_id: int, pet: dict):
    adoptions.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {
            "$set": {
                "pet_name": pet["Pet"],
                "pet_icon": pet["assets"]["icon"],
                "pet_emote": pet["assets"]["emote"],
            }
        },
        upsert=True
    )

def get_pet(guild_id: int, user_id: int):
    return adoptions.find_one({"guild_id": guild_id, "user_id": user_id})

def set_pet_nickname(guild_id: int, user_id: int, nickname: str):
    adoptions.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"pet_nickname": nickname}},
        upsert=False
    )

def remove_pet(guild_id: int, user_id: int):
    result = adoptions.delete_one({"guild_id": guild_id, "user_id": user_id})
    return result.deleted_count > 0