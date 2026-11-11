import os
import random
import requests
from io import BytesIO
from PIL import Image

# CONFIGURATION
CUBE_COBRA_ID = "6fa7c556-19c8-4efc-b34e-11bf188b990e"  # Your Full ID
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def generate_and_send_p1p1():
    if not WEBHOOK_URL:
        raise ValueError("DISCORD_WEBHOOK_URL environment variable is missing.")

    # 1. Fetch Cube data from Cube Cobra
    url = f"https://cubecobra.com/cube/api/cubejson/{CUBE_COBRA_ID}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"Failed to fetch cube: HTTP {res.status_code}")
    
    cards = res.json().get("cards", {}).get("mainboard", [])
    if len(cards) < 15:
        raise Exception("Not enough cards in cube to generate a booster pack.")

    # 2. Pick 15 random unique cards
    pack = random.sample(cards, 15)

    # 3. Format text list with Scryfall links
    col1, col2 = [], []
    card_images = []
