import os
from typing import List

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")

# Admin user IDs (replace with actual admin user IDs)
ADMIN_IDS: List[int] = [
    int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",") if x.strip()
]

# Database file paths
CONFIG_FILE = "data/config.json"
MENU_FILE = "data/menu.json"

# Bot settings
MAX_ORDERS_PER_USER = 5
ORDER_TIMEOUT_HOURS = 24

# Messages and emojis
RESTAURANT_NAME = "𝐓𝐡𝐞 𝐊𝐫𝐮𝐬𝐭𝐲 𝐊𝐫𝐚𝐛 • 𝐍𝐞𝐨𝐭𝐞𝐜𝐧𝐨"
WELCOME_MESSAGE = f"""
🦀 Benvenuto al {RESTAURANT_NAME}! 🦀

🏠 Il miglior ristorante sottomarino di Bikini Bottom!

🍔 Usa /menu per vedere il nostro delizioso menù
📣 Usa /sponsor per richiedere uno sponsor
📝 Usa /curriculum per candidarti a lavorare con noi

✨ Tutto è puramente roleplay e divertimento! ✨
"""

# Emoji constants
EMOJI = {
    'burger': '🍔',
    'drink': '🥤',
    'extra': '🍟',
    'back': '🔙',
    'confirm': '✔️',
    'cancel': '❌',
    'order': '📦',
    'sponsor': '📣',
    'curriculum': '📝',
    'pending': '⏳',
    'preparing': '🔥',
    'ready': '✅',
    'rejected': '❌',
    'approved': '✅',
    'reply': '💬'
}
