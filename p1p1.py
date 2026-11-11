import os
import random
import requests

# CONFIGURATION
CUBE_COBRA_ID = "vintagecube"  # Replace with your Cube Cobra ID slug
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

    # 3. Format cards with Scryfall links
    col1, col2 = [], []
    for idx, card in enumerate(pack, 1):
        name = card.get("details", {}).get("name", "Unknown Card")
        scryfall_link = f"https://scryfall.com/search?q={requests.utils.quote(name)}"
        entry = f"**{idx}.** [{name}]({scryfall_link})"
        
        if idx <= 8:
            col1.append(entry)
        else:
            col2.append(entry)

    # 4. Build Discord Webhook Payload
    first_card_name = pack[0].get("details", {}).get("name", "")
    image_url = f"https://api.scryfall.com/cards/named?exact={requests.utils.quote(first_card_name)}&format=image"

    embed = {
        "title": "⚔️ Daily Pack 1, Pick 1 ⚔️",
        "description": f"Here is today's P1P1 from **{CUBE_COBRA_ID}**! Reply below with your pick and reasoning.",
        "color": 15844367,  # Gold color
        "fields": [
            {"name": "Cards 1–8", "value": "\n".join(col1), "inline": True},
            {"name": "Cards 9–15", "value": "\n".join(col2), "inline": True}
        ],
        "image": {"url": image_url},
        "footer": {"text": "Click any card name to open its Scryfall page!"}
    }

    payload = {
        "username": "P1P1 Bot",
        "embeds": [embed]
    }

    # 5. Send to Discord
    post_res = requests.post(WEBHOOK_URL, json=payload)
    if post_res.status_code in [200, 204]:
        print("P1P1 successfully posted to Discord!")
    else:
        print(f"Failed to post webhook: {post_res.status_code} - {post_res.text}")

if __name__ == "__main__":
    generate_and_send_p1p1()
