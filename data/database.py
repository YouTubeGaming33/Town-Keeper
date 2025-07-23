# Required Library(s) and Import(s)
import os

from pymongo import MongoClient

# Pulls MONGO=DB URI from .env - If not found then Raises ValueError.
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("No MongoDB URI found in environment variables")

# Setting up Database, Client and Collections.
client = MongoClient(MONGO_URI)
db = client["test"]