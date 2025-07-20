from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command

from config import WELCOME_MESSAGE, EMOJI
from utils.keyboards import MenuKeyboard
from database import Database

router = Router()

async def handle_unknown_message(message: Message, db: Database):
    """Handle any unrecognized message"""
    response_text = f"🤖 Non ho capito il tuo messaggio!\n\n"
    response_text += f"🔧 **Comandi disponibili:**\n"
    response_text += f"• /start - Messaggio di benvenuto\n"
    response_text += f"• /menu - Visualizza il menù\n"
    response_text += f"• /sponsor - Richiedi sponsor\n"
    response_text += f"• /curriculum - Invia candidatura\n\n"
    response_text += f"💡 Oppure usa i bottoni qui sotto:"

    await message.answer(
        response_text,
        reply_markup=MenuKeyboard.help_menu()
    )

def register_handlers(dp, db: Database, bot: Bot):
    """Register fallback handlers - should be registered LAST"""

    @dp.message()
    async def fallback_handler(message: Message):
        # Check if user is banned
        if db.is_user_banned(message.from_user.id):
            await message.answer("🚫 Sei stato bannato dal bot!")
            return

        await handle_unknown_message(message, db)