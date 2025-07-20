
from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from utils.keyboards import RecruitmentKeyboard
from database import Database
from handlers.states import ReplyStates

router = Router()

async def cmd_list_users(message: Message, db: Database, bot: Bot):
    """List all registered users"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Non hai i permessi per questo comando!")
        return
    
    users = db.get_all_users()
    if not users:
        await message.answer("`❌ Nessun utente registrato`")
        return
    
    # Send to users topic
    users_topic_id = db.get_topic_id("users")
    staff_group_id = db.get_staff_group_id()
    
    if staff_group_id and users_topic_id:
        for user_id, user_data in users.items():
            minecraft_name = user_data.get("minecraft_name", "N/A")
            username = user_data.get("username", "N/A")
            banned = user_data.get("banned", False)
            status = "🚫 Bannato" if banned else "✅ Attivo"
            
            user_text = f"`👤` **`Utente: {username}`**\n\n"
            user_text += f"`🆔` **`ID:`** `{user_id}`\n"
            user_text += f"`🎮` **`Minecraft:`** `{minecraft_name}`\n"
            user_text += f"`📊` **`Stato:`** {status}\n"
            user_text += f"`📅` **`Registrato:`** `{user_data.get('registered_at', 'N/A')[:10]}`"
            
            await bot.send_message(
                chat_id=staff_group_id,
                message_thread_id=users_topic_id,
                text=user_text,
                reply_markup=RecruitmentKeyboard.user_management_actions(user_id, banned)
            )

async def handle_ban_user(callback: CallbackQuery, db: Database, bot: Bot):
    """Handle user ban"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Non autorizzato!", show_alert=True)
        return
    
    user_id = int(callback.data.split(":")[-1])
    db.ban_user(user_id)
    
    try:
        await callback.message.edit_text(
            callback.message.text.replace("✅ Attivo", "🚫 Bannato"),
            reply_markup=RecruitmentKeyboard.user_management_actions(str(user_id), True)
        )
        
        # Notify user
        await bot.send_message(
            chat_id=user_id,
            text="`🚫` **`Sei stato bannato dal bot`**\n\n`Non puoi più usare i comandi.`"
        )
    except Exception as e:
        print(f"Error banning user: {e}")
    
    await callback.answer("✅ Utente bannato!")

async def handle_unban_user(callback: CallbackQuery, db: Database, bot: Bot):
    """Handle user unban"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Non autorizzato!", show_alert=True)
        return
    
    user_id = int(callback.data.split(":")[-1])
    db.unban_user(user_id)
    
    try:
        await callback.message.edit_text(
            callback.message.text.replace("🚫 Bannato", "✅ Attivo"),
            reply_markup=RecruitmentKeyboard.user_management_actions(str(user_id), False)
        )
        
        # Notify user
        await bot.send_message(
            chat_id=user_id,
            text="`✅` **`Sei stato sbannato dal bot`**\n\n`Puoi tornare ad usare tutti i comandi.`"
        )
    except Exception as e:
        print(f"Error unbanning user: {e}")
    
    await callback.answer("✅ Utente sbannato!")

def register_handlers(dp, db: Database, bot: Bot):
    """Register user management handlers"""
    
    @dp.message(Command("list_users"))
    async def list_users_handler(message: Message):
        await cmd_list_users(message, db, bot)
    
    @dp.callback_query(lambda c: c.data.startswith("ban_user:"))
    async def ban_user_handler(callback: CallbackQuery):
        await handle_ban_user(callback, db, bot)
    
    @dp.callback_query(lambda c: c.data.startswith("unban_user:"))
    async def unban_user_handler(callback: CallbackQuery):
        await handle_unban_user(callback, db, bot)
