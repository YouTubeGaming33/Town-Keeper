# Required Library(s)
import json

# Loads pet.json File.
def load_pets():
    with open("data/pet.json", "r", encoding="utf-8") as f:
        return json.load(f)