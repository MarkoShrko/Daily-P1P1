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
    
    for idx, card in enumerate(pack, 1):
        name = card.get("details", {}).get("name", "Unknown Card")
        scryfall_link = f"https://scryfall.com/search?q={requests.utils.quote(name)}"
        entry = f"**{idx}.** [{name}]({scryfall_link})"
        
        if idx <= 8:
            col1.append(entry)
        else:
            col2.append(entry)

        # Fetch image for grid compilation
        img_url = f"https://api.scryfall.com/cards/named?exact={requests.utils.quote(name)}&format=image&version=normal"
        img_res = requests.get(img_url)
        if img_res.status_code == 200:
            card_images.append(Image.open(BytesIO(img_res.content)).convert("RGB"))

    # 4. Create a 3x5 Image Montage Grid using Pillow
    if card_images:
        card_w, card_h = 200, 280
        resized_images = [img.resize((card_w, card_h)) for img in card_images]

        cols = 5
        rows = 3
        grid_width = cols * card_w
        grid_height = rows * card_h
        
        montage = Image.new('RGB', (grid_width, grid_height), (43, 45, 49))
        
        for i, img in enumerate(resized_images):
            r = i // cols
            c = i % cols
            montage.paste(img, (c * card_w, r * card_h))

        buffer = BytesIO()
        montage.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        image_bytes = buffer.read()
    else:
        image_bytes = None

    # 5. Build Discord Webhook Payload & File Attachment
    embed = {
        "title": "⚔️ Daily Pack 1, Pick 1 ⚔️",
        "description": f"Here is today's P1P1! Review the visual grid below and reply with your pick and reasoning.",
        "color": 15844367,
        "fields": [
            {"name": "Cards 1–8", "value": "\n".join(col1), "inline": True},
            {"name": "Cards 9–15", "value": "\n".join(col2), "inline": True}
        ],
        "image": {"url": "attachment://p1p1_grid.jpg"},
        "footer": {"text": "Click any card name above to open its Scryfall page!"}
    }

    payload = {
        "username": "P1P1 Bot",
        "embeds": [embed]
    }

    files = {
        "payload_json": (None, requests.compat.json.dumps(payload)),
        "files[0]": ("p1p1_grid.jpg", image_bytes, "image/jpeg")
    }

    post_res = requests.post(WEBHOOK_URL, files=files)
    if post_res.status_code in [200, 204]:
        print("P1P1 grid successfully posted to Discord!")
    else:
        print(f"Failed to post webhook: {post_res.status_code} - {post_res.text}")

if __name__ == "__main__":
    generate_and_send_p1p1()
