from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext

from config import EMOJI, ADMIN_IDS
from utils.keyboards import SponsorKeyboard
from database import Database
from handlers.states import SponsorStates

router = Router()

async def cmd_sponsor(message: Message, db: Database, state: FSMContext):
    """Handle /sponsor command"""
    # Check if user has minecraft name
    minecraft_name = db.get_user_minecraft_name(message.from_user.id)
    if not minecraft_name:
        await message.answer(
            "⚠️ **`Nome Minecraft Richiesto`**\n\n"
            "`Per richiedere sponsor devi prima registrare il tuo nome Minecraft.`\n\n"
            "`Scrivi il tuo nome Minecraft:`"
        )
        await state.set_state(SponsorStates.waiting_for_minecraft_name)
        return
    
    sponsor_text = f"📣 **`Richiesta Sponsor - {message.from_user.full_name}`**\n\n"
    sponsor_text += "`🎯` **`Come funziona:`**\n"
    sponsor_text += "`•` `Lo sponsor è completamente roleplay`\n"
    sponsor_text += "`•` `Prima devi specificare ore e durata`\n"
    sponsor_text += "`•` `Poi dovrai inviare/inoltrare il messaggio`\n"
    sponsor_text += "`•` `Infine foto del 'pagamento' (roleplay)`\n"
    sponsor_text += "`•` `Lo staff valuterà la tua richiesta`\n\n"
    sponsor_text += "`💡` **`Primo Passo:`** `Scrivi quante ore vuoi sponsorizzare e se è un messaggio fissato:`\n\n"
    sponsor_text += "`Esempio: 24 ore, messaggio fissato`"
    
    await message.answer(sponsor_text)
    await state.set_state(SponsorStates.waiting_for_hours_info)

async def handle_forward_message(message: Message, state: FSMContext, db: Database):
    """Handle forwarded message for sponsor request"""
    if not message.text and not message.caption:
        await message.answer(
            "❌ Il messaggio deve contenere del testo!\n"
            "Invia o inoltra un messaggio con la tua proposta di sponsor."
        )
        return
    
    # Store the message content and message info for forwarding
    sponsor_content = message.text or message.caption
    await state.update_data(
        sponsor_message=sponsor_content,
        original_message_id=message.message_id,
        original_chat_id=message.chat.id
    )
    
    await message.answer(
        "✅ **Messaggio ricevuto!**\n\n"
        "📸 **Secondo Passo**: Ora invia una foto che mostri il 'pagamento' per lo sponsor (roleplay):"
    )
    await state.set_state(SponsorStates.waiting_for_payment_photo)

async def handle_payment_photo(message: Message, state: FSMContext, db: Database, bot: Bot):
    """Handle payment photo for sponsor request"""
    if not message.photo:
        await message.answer(
            "❌ Devi inviare una foto!\n"
            "Invia una foto che mostri il 'pagamento' per lo sponsor."
        )
        return
    
    data = await state.get_data()
    sponsor_message = data.get('sponsor_message', 'Nessun messaggio')
    original_message_id = data.get('original_message_id')
    original_chat_id = data.get('original_chat_id')
    username = message.from_user.username or message.from_user.full_name
    
    # Create sponsor request with message content and forwarding info
    sponsor_id = db.create_sponsor_request(
        message.from_user.id, 
        username, 
        sponsor_message, 
        original_message_id, 
        original_chat_id
    )
    
    await state.clear()
    
    # Send confirmation to user
    await message.answer(
        f"✅ **Richiesta Sponsor Inviata!**\n\n"
        f"🆔 ID Richiesta: `{sponsor_id}`\n"
        f"⏳ Stato: In attesa di valutazione\n\n"
        f"Ti contatteremo presto con una risposta!",
        reply_markup=SponsorKeyboard.back_to_menu()
    )
    
    # Send to staff group if configured
    staff_group_id = db.get_staff_group_id()
    sponsors_topic_id = db.get_topic_id("sponsors")
    
    if staff_group_id:
        try:
            staff_text = f"📣 **Nuova Richiesta Sponsor**\n\n"
            staff_text += f"👤 Da: @{username}\n"
            staff_text += f"🆔 ID: `{sponsor_id}`\n"
            staff_text += f"📅 Data: {message.date.strftime('%d/%m/%Y %H:%M')}\n\n"
            staff_text += f"💡 **Proposta:**\n{sponsor_message}\n\n"
            staff_text += f"📸 **Foto pagamento ricevuta**\n"
            staff_text += f"⏳ **Stato:** In attesa"
            
            # Send text message to staff group
            if sponsors_topic_id:
                staff_message = await bot.send_message(
                    chat_id=staff_group_id,
                    message_thread_id=sponsors_topic_id,
                    text=staff_text,
                    reply_markup=SponsorKeyboard.staff_sponsor_actions(sponsor_id)
                )
                
                # Forward the original sponsor message
                if original_message_id and original_chat_id:
                    await bot.forward_message(
                        chat_id=staff_group_id,
                        from_chat_id=original_chat_id,
                        message_id=original_message_id,
                        message_thread_id=sponsors_topic_id
                    )
                
                # Send the payment photo as separate message
                await bot.forward_message(
                    chat_id=staff_group_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                    message_thread_id=sponsors_topic_id
                )
            else:
                staff_message = await bot.send_message(
                    chat_id=staff_group_id,
                    text=staff_text,
                    reply_markup=SponsorKeyboard.staff_sponsor_actions(sponsor_id)
                )
                
                # Forward the original sponsor message
                if original_message_id and original_chat_id:
                    await bot.forward_message(
                        chat_id=staff_group_id,
                        from_chat_id=original_chat_id,
                        message_id=original_message_id
                    )
                
                # Send the payment photo as separate message
                await bot.forward_message(
                    chat_id=staff_group_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id
                )
            
            # Save staff message ID
            db.set_sponsor_staff_message(sponsor_id, staff_message.message_id)
            
        except Exception as e:
            print(f"Error sending sponsor request to staff group: {e}")
    
    # Message handlers don't need callback.answer()

async def handle_sponsor_cancel(callback: CallbackQuery, db: Database):
    """Handle sponsor request cancellation"""
    try:
        await callback.message.edit_text(
            "❌ **Richiesta Sponsor Annullata**\n\n"
            "Puoi sempre fare una nuova richiesta quando vuoi!",
            reply_markup=SponsorKeyboard.back_to_menu()
        )
    except TelegramBadRequest:
        pass
    
    await callback.answer("❌ Richiesta annullata")

async def handle_staff_sponsor_action(callback: CallbackQuery, db: Database, bot: Bot):
    """Handle staff sponsor actions"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Non hai i permessi per questa azione!", show_alert=True)
        return
    
    action_data = callback.data.split(":")
    action = action_data[1]
    sponsor_id = action_data[2]
    
    sponsor = db.get_sponsor_request(sponsor_id)
    if not sponsor:
        await callback.answer("❌ Richiesta sponsor non trovata!", show_alert=True)
        return
    
    if action == "approve":
        db.update_sponsor_status(sponsor_id, "approved")
        status_text = "✅ Approvato"
        user_message = f"🎉 La tua richiesta sponsor `{sponsor_id}` è stata approvata! Ti contatteremo presto per i dettagli."
        
        # Send to sponsor channel if configured
        sponsor_channel_id = db.get_sponsor_channel_id()
        if sponsor_channel_id:
            try:
                # Forward the original message to sponsor channel
                original_chat_id = sponsor.get('original_chat_id')
                original_message_id = sponsor.get('original_message_id')
                
                if original_chat_id and original_message_id:
                    # Forward the original message with images/media
                    await bot.forward_message(
                        chat_id=sponsor_channel_id,
                        from_chat_id=original_chat_id,
                        message_id=original_message_id
                    )
                else:
                    # Fallback to text message if forwarding info not available
                    await bot.send_message(
                        chat_id=sponsor_channel_id,
                        text=sponsor.get('message', 'Messaggio sponsor non disponibile')
                    )
            except Exception as e:
                print(f"Error sending to sponsor channel: {e}")
        
    elif action == "reject":
        db.update_sponsor_status(sponsor_id, "rejected")
        status_text = "❌ Rifiutato"
        user_message = f"❌ La tua richiesta sponsor `{sponsor_id}` è stata rifiutata. Grazie comunque per l'interesse!"
    
    # Update staff message
    try:
        staff_text = f"📣 **Richiesta Sponsor Aggiornata**\n\n"
        staff_text += f"👤 Da: @{sponsor['username']}\n"
        staff_text += f"🆔 ID: `{sponsor_id}`\n"
        staff_text += f"📅 Data: {sponsor['created_at'][:10]}\n\n"
        staff_text += f"💡 **Dettaglio:** Richiesta sponsor generico\n"
        staff_text += f"📊 **Stato:** {status_text}"
        
        # Remove keyboard after action
        await callback.message.edit_text(
            staff_text,
            reply_markup=None
        )
        
    except TelegramBadRequest:
        pass
    
    # Send notification to user
    try:
        await bot.send_message(
            chat_id=sponsor["user_id"],
            text=user_message
        )
    except Exception as e:
        print(f"Error sending notification to user: {e}")
    
    await callback.answer(f"✅ Richiesta {action}!")

async def handle_minecraft_name_sponsor(message: Message, state: FSMContext, db: Database):
    """Handle minecraft name input for sponsor"""
    minecraft_name = message.text.strip()
    
    # Save minecraft name
    db.set_user_minecraft_name(
        message.from_user.id, 
        minecraft_name, 
        message.from_user.username or message.from_user.full_name
    )
    
    await message.answer(
        f"`✅` **`Nome Minecraft salvato: {minecraft_name}`**\n\n"
        "`💡` **`Ora specifica ore e durata:`**\n\n"
        "`Esempio: 24 ore, messaggio fissato`"
    )
    await state.set_state(SponsorStates.waiting_for_hours_info)

async def handle_hours_info(message: Message, state: FSMContext, db: Database):
    """Handle hours and duration info for sponsor"""
    hours_info = message.text.strip()
    await state.update_data(hours_info=hours_info)
    
    await message.answer(
        f"`✅` **`Durata salvata: {hours_info}`**\n\n"
        "`🔄` **`Secondo Passo:`** `Invia o inoltra un messaggio con la tua proposta di sponsor:`"
    )
    await state.set_state(SponsorStates.waiting_for_forward_message)

def register_handlers(dp, db: Database, bot: Bot):
    """Register sponsor handlers"""
    
    @dp.message(Command("sponsor"))
    async def sponsor_handler(message: Message, state: FSMContext):
        await cmd_sponsor(message, db, state)
    
    @dp.message(SponsorStates.waiting_for_minecraft_name)
    async def minecraft_name_sponsor_handler(message: Message, state: FSMContext):
        await handle_minecraft_name_sponsor(message, state, db)
    
    @dp.message(SponsorStates.waiting_for_hours_info)
    async def hours_info_handler(message: Message, state: FSMContext):
        await handle_hours_info(message, state, db)
    
    @dp.message(SponsorStates.waiting_for_forward_message)
    async def forward_message_handler(message: Message, state: FSMContext):
        await handle_forward_message(message, state, db)
    
    @dp.message(SponsorStates.waiting_for_payment_photo)
    async def payment_photo_handler(message: Message, state: FSMContext):
        await handle_payment_photo(message, state, db, bot)
    
    @dp.callback_query(lambda c: c.data == "request_sponsor")
    async def sponsor_request_handler(callback: CallbackQuery, state: FSMContext):
        await cmd_sponsor(callback.message, db, state)
        await callback.answer()
    
    @dp.callback_query(lambda c: c.data == "cancel_sponsor")
    async def sponsor_cancel_handler(callback: CallbackQuery):
        await handle_sponsor_cancel(callback, db)
    
    @dp.callback_query(lambda c: c.data.startswith("sponsor_action:"))
    async def staff_sponsor_handler(callback: CallbackQuery):
        await handle_staff_sponsor_action(callback, db, bot)
