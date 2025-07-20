from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from config import WELCOME_MESSAGE, EMOJI
from utils.keyboards import MenuKeyboard
from database import Database

router = Router()

async def cmd_start(message: Message, db: Database):
    """Handle /start command"""
    await message.answer(
        WELCOME_MESSAGE,
        reply_markup=MenuKeyboard.home_menu()
    )

async def cmd_menu(message: Message, db: Database):
    """Handle /menu command"""
    menu_data = db.get_menu()
    categories = db.get_categories()
    
    if not categories:
        await message.answer("❌ Il menù non è ancora disponibile.")
        return
    
    cart_count = db.get_cart_count(message.from_user.id)
    cart_text = f"\n\n🛒 Carrello: {cart_count} elementi" if cart_count > 0 else ""
    
    await message.answer(
        f"🍔 **Menù del {menu_data.get('restaurant_name', 'Ristorante')}**\n\n"
        f"Scegli una categoria:{cart_text}",
        reply_markup=MenuKeyboard.categories(categories, cart_count > 0)
    )

async def handle_category_selection(callback: CallbackQuery, db: Database):
    """Handle category selection"""
    category = callback.data.split(":")[-1]
    items = db.get_category_items(category)
    
    if not items:
        await callback.answer("❌ Categoria vuota!", show_alert=True)
        return
    
    cart_count = db.get_cart_count(callback.from_user.id)
    cart_text = f"\n\n🛒 Carrello: {cart_count} elementi" if cart_count > 0 else ""
    
    try:
        await callback.message.edit_text(
            f"📋 **{category}**\n\n"
            f"Scegli un piatto:{cart_text}",
            reply_markup=MenuKeyboard.items(category, items, cart_count > 0)
        )
    except TelegramBadRequest:
        pass
    
    await callback.answer()

async def handle_item_selection(callback: CallbackQuery, db: Database):
    """Handle item selection - add to cart"""
    data_parts = callback.data.split(":")
    category = data_parts[1]
    item_name = data_parts[2]
    
    items = db.get_category_items(category)
    if item_name not in items:
        await callback.answer("❌ Piatto non trovato!", show_alert=True)
        return
    
    item_data = items[item_name]
    item_price = item_data["price"]
    
    # Add to cart
    db.add_to_cart(callback.from_user.id, item_name, item_price, category)
    
    await callback.answer(f"✅ {item_name} aggiunto al carrello!", show_alert=True)
    
    # Update the message to show new cart count
    cart_count = db.get_cart_count(callback.from_user.id)
    cart_text = f"\n\n🛒 Carrello: {cart_count} elementi" if cart_count > 0 else ""
    
    try:
        await callback.message.edit_text(
            f"📋 **{category}**\n\n"
            f"Scegli un piatto:{cart_text}",
            reply_markup=MenuKeyboard.items(category, items, cart_count > 0)
        )
    except TelegramBadRequest:
        pass

async def handle_view_cart(callback: CallbackQuery, db: Database):
    """Handle view cart action"""
    cart = db.get_user_cart(callback.from_user.id)
    
    if not cart:
        await callback.answer("🛒 Il tuo carrello è vuoto!", show_alert=True)
        return
    
    cart_text = "🛒 **Il tuo carrello:**\n\n"
    total = 0
    
    for item in cart:
        item_total = item["item_price"] * item["quantity"]
        total += item_total
        cart_text += f"• {item['item_name']} x{item['quantity']} - {item_total}€\n"
    
    cart_text += f"\n💰 **Totale: {total}€**"
    
    try:
        await callback.message.edit_text(
            cart_text,
            reply_markup=MenuKeyboard.cart_actions()
        )
    except TelegramBadRequest:
        pass
    
    await callback.answer()

async def handle_clear_cart(callback: CallbackQuery, db: Database):
    """Handle clear cart action"""
    db.clear_cart(callback.from_user.id)
    await callback.answer("🗑️ Carrello svuotato!", show_alert=True)
    
    # Go back to main menu
    await cmd_menu(callback.message, db)

async def handle_back_to_menu(callback: CallbackQuery, db: Database):
    """Handle back to menu action"""
    await cmd_menu(callback.message, db)
    await callback.answer()

async def handle_back_to_categories(callback: CallbackQuery, db: Database):
    """Handle back to categories action"""
    categories = db.get_categories()
    cart_count = db.get_cart_count(callback.from_user.id)
    cart_text = f"\n\n🛒 Carrello: {cart_count} elementi" if cart_count > 0 else ""
    
    try:
        await callback.message.edit_text(
            f"🍔 **Menù del Ristorante**\n\n"
            f"Scegli una categoria:{cart_text}",
            reply_markup=MenuKeyboard.categories(categories, cart_count > 0)
        )
    except TelegramBadRequest:
        pass
    
    await callback.answer()

async def handle_back_to_home(callback: CallbackQuery, db: Database):
    """Handle back to home"""
    try:
        await callback.message.edit_text(
            "🏠 **Benvenuto al The Krusty Krab • Neotecno!**\n\n"
            "🍔 Il miglior ristorante virtuale per il roleplay!\n\n"
            "Cosa vuoi fare oggi?",
            reply_markup=MenuKeyboard.home_menu()
        )
    except TelegramBadRequest:
        pass
    
    await callback.answer()

async def handle_help(callback: CallbackQuery, db: Database):
    """Handle help"""
    help_text = """ℹ️ **Aiuto - The Krusty Krab**

🍔 **Menu**: Sfoglia il nostro menu e aggiungi piatti al carrello

📣 **Sponsor**: Richiedi sponsorizzazioni per eventi (roleplay)
   • Devi prima inviare/inoltrare un messaggio
   • Serve foto di pagamento per confermare

📝 **Candidatura**: Candidati per lavorare nel ristorante
   • Compila il curriculum virtuale
   • Lo staff valuterà la tua richiesta

🛒 **Ordini**: Per confermare un ordine serve la foto del pagamento

💡 **Nota**: Tutto è completamente roleplay - nessun pagamento reale!"""
    
    try:
        await callback.message.edit_text(
            help_text,
            reply_markup=MenuKeyboard.home_menu()
        )
    except TelegramBadRequest:
        pass
    
    await callback.answer()

def register_handlers(dp, db: Database, bot: Bot):
    """Register menu handlers"""
    
    @dp.message(Command("start"))
    async def start_handler(message: Message):
        await cmd_start(message, db)
    
    @dp.message(Command("menu"))
    async def menu_handler(message: Message):
        await cmd_menu(message, db)
    
    @dp.callback_query(lambda c: c.data == "main_menu")
    async def main_menu_handler(callback: CallbackQuery):
        await cmd_menu(callback.message, db)
        await callback.answer()
    
    @dp.callback_query(lambda c: c.data.startswith("category:"))
    async def category_handler(callback: CallbackQuery):
        await handle_category_selection(callback, db)
    
    @dp.callback_query(lambda c: c.data.startswith("item:"))
    async def item_handler(callback: CallbackQuery):
        await handle_item_selection(callback, db)
    
    @dp.callback_query(lambda c: c.data == "view_cart")
    async def cart_handler(callback: CallbackQuery):
        await handle_view_cart(callback, db)
    
    @dp.callback_query(lambda c: c.data == "clear_cart")
    async def clear_cart_handler(callback: CallbackQuery):
        await handle_clear_cart(callback, db)
    
    @dp.callback_query(lambda c: c.data == "back_to_menu")
    async def back_menu_handler(callback: CallbackQuery):
        await handle_back_to_menu(callback, db)
    
    @dp.callback_query(lambda c: c.data == "back_to_categories")
    async def back_categories_handler(callback: CallbackQuery):
        await handle_back_to_categories(callback, db)
    
    @dp.callback_query(lambda c: c.data == "back_to_home")
    async def back_home_handler(callback: CallbackQuery):
        await handle_back_to_home(callback, db)
    
    @dp.callback_query(lambda c: c.data == "help")
    async def help_handler(callback: CallbackQuery):
        await handle_help(callback, db)
