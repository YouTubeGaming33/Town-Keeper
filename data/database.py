# Required Library(s) and Import(s)
import os
import json

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

# Used to check if Item exists.
with open("data/food.json", "r") as f:
    ITEM_DEFINITIONS = {item["name"].capitalize(): item for item in json.load(f)}

items_collection = db["items"]  # MongoDB collection

with open("data/food.json", "r") as f:
    food_items = json.load(f)  # Load JSON into a separate variable

for item in food_items:
    items_collection.update_one(
        {"name": item["name"]},  # Match by name (case sensitive)
        {"$set": item},
        upsert=True
    )


def add_item_to_user(guild_id, user_id, item_name, quantity=1):
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

def adopt_pet(user_id: int, guild_id: int, pet: dict):
    adoptions.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {
            "$set": {
                "pet_name": pet["Pet"],
                "pet_icon": pet["assets"]["icon"],
                "pet_emote": pet["assets"]["emote"],
                "health": "❤️❤️❤️❤️❤️",
                "hunger": "🍔🍔🍔🍔🍔"
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