from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext

from config import EMOJI, ADMIN_IDS
from utils.keyboards import OrderKeyboard
from database import Database
from handlers.states import OrderStates

router = Router()

async def handle_checkout(callback: CallbackQuery, db: Database, bot: Bot):
    """Handle checkout process"""
    cart = db.get_user_cart(callback.from_user.id)
    
    if not cart:
        await callback.answer("🛒 Il tuo carrello è vuoto!", show_alert=True)
        return
    
    # Check if user has minecraft name
    minecraft_name = db.get_user_minecraft_name(callback.from_user.id)
    if not minecraft_name:
        try:
            await callback.message.edit_text(
                "⚠️ **`Nome Minecraft Richiesto`**\n\n"
                "`Per effettuare ordini devi prima registrare il tuo nome Minecraft.`\n\n"
                "`Scrivi il tuo nome Minecraft:`",
                reply_markup=OrderKeyboard.cancel_order()
            )
        except TelegramBadRequest:
            pass
        
        await callback.answer()
        return
    
    total = db.get_cart_total(callback.from_user.id)
    
    # Show order confirmation
    order_text = "📋 **Conferma il tuo ordine:**\n\n"
    
    for item in cart:
        item_total = item["item_price"] * item["quantity"]
        order_text += f"• {item['item_name']} x{item['quantity']} - {item_total}€\n"
    
    order_text += f"\n💰 **Totale: {total}€**\n\n"
    order_text += "⚠️ **Importante**: Per confermare l'ordine dovrai inviare una foto del pagamento (roleplay).\n\n"
    order_text += "Vuoi procedere?"
    
    try:
        await callback.message.edit_text(
            order_text,
            reply_markup=OrderKeyboard.confirm_order()
        )
    except TelegramBadRequest:
        pass
    
    await callback.answer()

async def handle_confirm_order(callback: CallbackQuery, db: Database, state: FSMContext):
    """Handle order confirmation - request payment photo"""
    try:
        await callback.message.edit_text(
            "📸 **Foto Pagamento Richiesta**\n\n"
            "Invia una foto che mostri il pagamento per l'ordine (roleplay).\n"
            "Una volta ricevuta la foto, l'ordine sarà confermato e inviato al nostro staff!"
        )
    except TelegramBadRequest:
        pass
    
    await callback.answer()
    await state.set_state(OrderStates.waiting_for_payment_photo)

async def handle_order_payment_photo(message: Message, state: FSMContext, db: Database, bot: Bot):
    """Handle payment photo for order"""
    if not message.photo:
        await message.answer(
            "❌ Devi inviare una foto!\n"
            "Invia una foto che mostri il pagamento per l'ordine."
        )
        return
    
    username = message.from_user.username or message.from_user.full_name
    
    # Create order from cart
    order_id = db.create_order_from_cart(message.from_user.id, username)
    
    if not order_id:
        await message.answer("❌ Errore nella creazione dell'ordine!")
        await state.clear()
        return
    
    order = db.get_order(order_id)
    await state.clear()
    
    # Send confirmation to user
    await message.answer(
        f"✅ **Ordine confermato!**\n\n"
        f"🆔 Numero ordine: `{order_id}`\n"
        f"⏳ Stato: In attesa\n"
        f"💰 Totale: {order['total_price']}€\n\n"
        f"📸 Foto di pagamento ricevuta!\n\n"
        f"Ti aggiorneremo sullo stato del tuo ordine!",
        reply_markup=OrderKeyboard.back_to_menu()
    )
    
    # Send order to staff group if configured
    staff_group_id = db.get_staff_group_id()
    orders_topic_id = db.get_topic_id("orders")
    
    if staff_group_id:
        try:
            # Create order message for staff
            staff_text = f"📦 **Nuovo Ordine**\n\n"
            staff_text += f"👤 Cliente: @{username}\n"
            staff_text += f"🆔 ID: `{order_id}`\n\n"
            
            for item in order["items"]:
                item_total = item["item_price"] * item["quantity"]
                staff_text += f"• {item['item_name']} x{item['quantity']} - {item_total}€\n"
            
            staff_text += f"\n💰 **Totale: {order['total_price']}€**\n"
            staff_text += f"📸 **Foto pagamento ricevuta**\n"
            staff_text += f"⏳ **Stato:** In attesa"
            
            # Send text message to staff group
            if orders_topic_id:
                staff_message = await bot.send_message(
                    chat_id=staff_group_id,
                    message_thread_id=orders_topic_id,
                    text=staff_text,
                    reply_markup=OrderKeyboard.staff_order_actions(order_id)
                )
                
                # Send the payment photo as separate message
                await bot.forward_message(
                    chat_id=staff_group_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                    message_thread_id=orders_topic_id
                )
            else:
                staff_message = await bot.send_message(
                    chat_id=staff_group_id,
                    text=staff_text,
                    reply_markup=OrderKeyboard.staff_order_actions(order_id)
                )
                
                # Send the payment photo as separate message
                await bot.forward_message(
                    chat_id=staff_group_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id
                )
            
            # Save staff message ID
            db.set_order_staff_message(order_id, staff_message.message_id)
            
        except Exception as e:
            print(f"Error sending order to staff group: {e}")
    
    # No callback answer needed for message handlers

async def handle_cancel_order(callback: CallbackQuery, db: Database):
    """Handle order cancellation"""
    # Go back to cart view
    from handlers.menu import handle_view_cart
    await handle_view_cart(callback, db)

async def handle_staff_order_action(callback: CallbackQuery, db: Database, bot: Bot):
    """Handle staff order actions"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Non hai i permessi per questa azione!", show_alert=True)
        return
    
    action_data = callback.data.split(":")
    action = action_data[1]
    order_id = action_data[2]
    
    order = db.get_order(order_id)
    if not order:
        await callback.answer("❌ Ordine non trovato!", show_alert=True)
        return
    
    if action == "accept":
        db.update_order_status(order_id, "preparing", callback.from_user.id)
        status_text = "🔥 In preparazione"
        user_message = f"🔥 Il tuo ordine `{order_id}` è ora in preparazione!"
        
    elif action == "ready":
        db.update_order_status(order_id, "ready", callback.from_user.id)
        status_text = "✅ Pronto"
        user_message = f"✅ Il tuo ordine `{order_id}` è pronto per il ritiro!"
        
    elif action == "complete":
        db.update_order_status(order_id, "completed", callback.from_user.id)
        status_text = "🎉 Completato"
        user_message = f"🎉 Il tuo ordine `{order_id}` è stato completato! Grazie!"
        
    elif action == "reject":
        db.update_order_status(order_id, "rejected", callback.from_user.id)
        status_text = "❌ Rifiutato"
        user_message = f"❌ Il tuo ordine `{order_id}` è stato rifiutato. Ci scusiamo per l'inconveniente."
    
    # Update staff message
    try:
        staff_text = f"📦 **Ordine Aggiornato**\n\n"
        staff_text += f"👤 Cliente: @{order['username']}\n"
        staff_text += f"🆔 ID: `{order_id}`\n\n"
        
        for item in order["items"]:
            item_total = item["item_price"] * item["quantity"]
            staff_text += f"• {item['item_name']} x{item['quantity']} - {item_total}€\n"
        
        staff_text += f"\n💰 **Totale: {order['total_price']}€**\n"
        staff_text += f"📊 **Stato:** {status_text}"
        
        # Update keyboard based on status
        if order["status"] in ["completed", "rejected"]:
            reply_markup = None
        else:
            reply_markup = OrderKeyboard.staff_order_actions(order_id)
        
        await callback.message.edit_text(
            staff_text,
            reply_markup=reply_markup
        )
        
    except TelegramBadRequest:
        pass
    
    # Send notification to user
    try:
        await bot.send_message(
            chat_id=order["user_id"],
            text=user_message
        )
    except Exception as e:
        print(f"Error sending notification to user: {e}")
    
    await callback.answer(f"✅ Ordine {action}!")

def register_handlers(dp, db: Database, bot: Bot):
    """Register order handlers"""
    
    @dp.callback_query(lambda c: c.data == "checkout")
    async def checkout_handler(callback: CallbackQuery):
        await handle_checkout(callback, db, bot)
    
    @dp.callback_query(lambda c: c.data == "confirm_order")
    async def confirm_order_handler(callback: CallbackQuery, state: FSMContext):
        await handle_confirm_order(callback, db, state)
    
    @dp.message(OrderStates.waiting_for_payment_photo)
    async def payment_photo_handler(message: Message, state: FSMContext):
        await handle_order_payment_photo(message, state, db, bot)
    
    @dp.callback_query(lambda c: c.data == "cancel_order")
    async def cancel_order_handler(callback: CallbackQuery):
        await handle_cancel_order(callback, db)
    
    @dp.callback_query(lambda c: c.data.startswith("order_action:"))
    async def staff_order_handler(callback: CallbackQuery):
        await handle_staff_order_action(callback, db, bot)
