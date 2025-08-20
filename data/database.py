# Required Library(s) and Import(s)
import os
import json
import time
import random

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
inventory = db["inventory"]
timers = db["timers"]
badges = db["badges"]

def get_random_food_item():
    with open("data/food.json", "r") as f:
        food_items = json.load(f)

    return random.choice(food_items)["name"].title()

# Used to check if Item exists.
with open("data/food.json", "r") as f:
    ITEM_DEFINITIONS = {item["name"].capitalize(): item for item in json.load(f)}

items_collection = db["items"]  # MongoDB collection

with open("data/food.json", "r") as f:
    food_items = json.load(f)  # Load JSON into a separate variable

for item in food_items:
    item["type"] = "food"  
    items_collection.update_one(
        {"name": item["name"]},  
        {"$set": item},          
        upsert=True
    )

def set_cooldown_timestamp(guild_id: int, user_id: int, command: str):
    """Stores the current timestamp for when a command was last used."""
    timestamp = int(time.time())
    timers.update_one(
        {"guild_id": guild_id, "user_id": user_id, "command": command},
        {"$set": {"last_used": timestamp}},
        upsert=True
    )

def get_time_since_last_use(guild_id: int, user_id: int, command: str):
    """Returns how many seconds ago the command was last used."""
    record = timers.find_one({"guild_id": guild_id, "user_id": user_id, "command": command})
    if not record or "last_used" not in record:
        return None  # Never used before
    return int(time.time()) - record["last_used"]

def add_item_to_user(guild_id, user_id, item_name, quantity):
    user = inventory.find_one({"user_id": str(user_id), "guild_id": str(guild_id)})

    if item_name not in ITEM_DEFINITIONS:
        return False

    if not user:
        inventory.insert_one({
            "user_id": str(user_id),
            "guild_id": str(guild_id),
            "inventory": [{"name": item_name, "quantity": quantity}]
        })
        return

    # Check if item already exists
    for inv_item in user["inventory"]:
        if inv_item["name"].lower() == item_name.lower():
            inv_item["quantity"] += quantity
            break
    else:
        # Add new item only if there are fewer than 9 item types
        if len(user["inventory"]) >= 9:
            return  # Or raise an error, or send feedback
        user["inventory"].append({"name": item_name, "quantity": quantity})

    inventory.update_one(
        {"user_id": str(user_id), "guild_id": str(guild_id)},
        {"$set": {"inventory": user["inventory"]}}
    )
    return True

def remove_item_from_user(guild_id, user_id, item_name, quantity=1):
    user = inventory.find_one({"user_id": str(user_id), "guild_id": str(guild_id)})
    if not user:
        return False

    for inv_item in user["inventory"]:
        if inv_item["name"].lower() == item_name.lower():
            if inv_item["quantity"] < quantity:
                return False
            inv_item["quantity"] -= quantity
            if inv_item["quantity"] == 0:
                user["inventory"].remove(inv_item)
            inventory.update_one(
                {"user_id": str(user_id), "guild_id": str(guild_id)},
                {"$set": {"inventory": user["inventory"]}}
            )
            return True
    return False

def get_user_inventory(guild_id, user_id):
    user = inventory.find_one({"user_id": str(user_id), "guild_id": str(guild_id)})
    if not user or not user.get("inventory"):
        return []
    return user["inventory"]

def get_distinct_item_count(guild_id, user_id):
    inventory_items = get_user_inventory(guild_id, user_id)
    return len(inventory_items)

def get_item(name):
    return db["items"].find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})

def set_happiness(user_id: int, guild_id: int, happiness: str):
    adoptions.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"happiness": happiness}},
        upsert=False
    )

def adopt_pet(user_id: int, guild_id: int, pet: dict):
    adoptions.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {
            "$set": {
                "pet_name": pet["Pet"],
                "pet_icon": pet["assets"]["icon"],
                "pet_emote": pet["assets"]["emote"],
                "health": "❤️❤️❤️❤️❤️",
                "hunger": "🍔🍔🍔🍔🍔",
                "happiness": "😄😄😄😄😄"
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