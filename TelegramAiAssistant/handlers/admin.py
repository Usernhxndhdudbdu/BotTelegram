from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from config import ADMIN_IDS
from utils.keyboards import AdminKeyboard
from handlers.states import AdminStates
from database import Database

router = Router()

def is_admin(user_id: int, db: Database) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS or db.is_admin(user_id)

async def cmd_setup_staff(message: Message, db: Database):
    """Setup staff group - admin only"""
    if not is_admin(message.from_user.id, db):
        await message.answer("❌ Non hai i permessi per questo comando!")
        return

    # Check if we're in a group
    if message.chat.type not in ['group', 'supergroup']:
        await message.answer(
            "⚠️ Questo comando deve essere usato in un gruppo!\n\n"
            "🔧 **Come configurare il gruppo staff:**\n"
            "1. Crea un supergruppo\n"
            "2. Aggiungi il bot come admin\n"
            "3. Abilita i Topics\n"
            "4. Usa questo comando nel gruppo"
        )
        return

    # Set this group as staff group
    db.set_staff_group_id(message.chat.id)

    await message.answer(
        f"✅ **Gruppo Staff Configurato!**\n\n"
        f"🆔 ID Gruppo: `{message.chat.id}`\n"
        f"📋 Ora usa /create_topics per creare i topics necessari"
    )

async def cmd_create_topics(message: Message, db: Database, bot: Bot):
    """Create forum topics in staff group"""
    if message.chat.type != "supergroup":
        await message.answer("❌ Questo comando funziona solo nei supergruppi!")
        return

    if not message.chat.is_forum:
        await message.answer("❌ Il gruppo deve avere i topic abilitati!")
        return

    topics = [
        ("📦 Ordini", "orders"),
        ("📜 Sponsor", "sponsors"), 
        ("📝 Candidature", "applications"),
        ("👥 Gestione Utenti", "users")
    ]

    created_topics = []

    for topic_name, topic_key in topics:
        try:
            # Check if topic already exists
            existing_topic_id = db.get_topic_id(topic_key)
            if existing_topic_id:
                created_topics.append(f"✅ {topic_name} (già esistente)")
                continue

            # Create forum topic
            topic = await bot.create_forum_topic(
                chat_id=message.chat.id,
                name=topic_name
            )

            # Save topic ID
            db.set_topic_id(topic_key, topic.message_thread_id)
            created_topics.append(f"✅ {topic_name}")

        except Exception as e:
            created_topics.append(f"❌ {topic_name} - Errore: {str(e)}")

    result_text = "📋 **Creazione Topics Completata**\n\n"
    result_text += "\n".join(created_topics)

    await message.answer(result_text)

async def cmd_gestisci_menu(message: Message, db: Database):
    """Manage menu - admin only"""
    if not is_admin(message.from_user.id, db):
        await message.answer("❌ Non hai i permessi per questo comando!")
        return

    categories = db.get_categories()

    menu_text = "⚙️ **Gestione Menù**\n\n"
    menu_text += "Scegli cosa vuoi fare:"

    await message.answer(
        menu_text,
        reply_markup=AdminKeyboard.menu_management(categories)
    )

async def cmd_aggiungi_piatto(message: Message, db: Database, state: FSMContext):
    """Add menu item - admin only"""
    if not is_admin(message.from_user.id, db):
        await message.answer("❌ Non hai i permessi per questo comando!")
        return

    categories = db.get_categories()

    await message.answer(
        "📝 **Aggiungi Nuovo Piatto**\n\n"
        "Step 1/4: Scegli la categoria:",
        reply_markup=AdminKeyboard.category_selection(categories)
    )

async def handle_category_for_new_item(callback: CallbackQuery, state: FSMContext):
    """Handle category selection for new item"""
    category = callback.data.split(":")[-1]
    await state.update_data(category=category)
    await state.set_state(AdminStates.waiting_for_item_name)

    try:
        await callback.message.edit_text(
            f"📝 **Aggiungi Nuovo Piatto**\n\n"
            f"Categoria: {category}\n"
            f"Step 2/4: Scrivi il nome del piatto:",
            reply_markup=AdminKeyboard.cancel_add_item()
        )
    except TelegramBadRequest:
        pass

    await callback.answer()

async def handle_item_name_input(message: Message, state: FSMContext):
    """Handle item name input"""
    await state.update_data(item_name=message.text)
    await state.set_state(AdminStates.waiting_for_item_price)

    data = await state.get_data()

    await message.answer(
        f"📝 **Aggiungi Nuovo Piatto**\n\n"
        f"Categoria: {data['category']}\n"
        f"Nome: {data['item_name']}\n"
        f"Step 3/4: Scrivi il prezzo (solo numeri):",
        reply_markup=AdminKeyboard.cancel_add_item()
    )

async def handle_item_price_input(message: Message, state: FSMContext):
    """Handle item price input"""
    try:
        price = int(message.text)
        await state.update_data(item_price=price)
        await state.set_state(AdminStates.waiting_for_item_description)

        data = await state.get_data()

        await message.answer(
            f"📝 **Aggiungi Nuovo Piatto**\n\n"
            f"Categoria: {data['category']}\n"
            f"Nome: {data['item_name']}\n"
            f"Prezzo: {price}€\n"
            f"Step 4/4: Scrivi la descrizione:",
            reply_markup=AdminKeyboard.cancel_add_item()
        )

    except ValueError:
        await message.answer(
            "❌ Prezzo non valido! Inserisci solo numeri.",
            reply_markup=AdminKeyboard.cancel_add_item()
        )

async def handle_item_description_input(message: Message, state: FSMContext, db: Database):
    """Handle item description input and create item"""
    data = await state.get_data()

    # Add item to menu
    db.add_menu_item(
        category=data['category'],
        name=data['item_name'],
        price=data['item_price'],
        description=message.text
    )

    await state.clear()

    await message.answer(
        f"✅ **Piatto Aggiunto!**\n\n"
        f"📋 Categoria: {data['category']}\n"
        f"🍽️ Nome: {data['item_name']}\n"
        f"💰 Prezzo: {data['item_price']}€\n"
        f"📝 Descrizione: {message.text}\n\n"
        f"Il piatto è ora disponibile nel menù!"
    )

async def handle_view_category(callback: CallbackQuery, db: Database):
    """Handle view category items"""
    category = callback.data.split(":")[-1]
    items = db.get_category_items(category)

    if not items:
        try:
            await callback.message.edit_text(
                f"📋 **{category}**\n\n"
                f"📋 Categoria vuota! Aggiungi il primo piatto:",
                reply_markup=AdminKeyboard.category_items_management(category, [])
            )
        except TelegramBadRequest:
            pass
        await callback.answer()
        return

    items_text = f"📋 **{category}**\n\n"
    for item_name, item_data in items.items():
        items_text += f"🍽️ **{item_name}**\n"
        items_text += f"💰 Prezzo: {item_data['price']}€\n"
        items_text += f"📝 {item_data.get('description', 'Nessuna descrizione')}\n\n"

    items_text += "Gestisci i piatti di questa categoria:"

    try:
        await callback.message.edit_text(
            items_text,
            reply_markup=AdminKeyboard.category_items_management(category, list(items.keys()))
        )
    except TelegramBadRequest:
        pass

    await callback.answer()

async def handle_remove_item(callback: CallbackQuery, db: Database):
    """Handle remove menu item"""
    data_parts = callback.data.split(":")
    category = data_parts[1]
    item_name = data_parts[2]

    # Remove item from database
    db.remove_menu_item(category, item_name)

    await callback.answer(f"🗑️ {item_name} rimosso!", show_alert=True)

    # Refresh the category view
    fake_callback = type('CallbackQuery', (), {
        'data': f'view_category:{category}',
        'message': callback.message,
        'answer': lambda: None
    })()
    await handle_view_category(fake_callback, db)

async def handle_back_to_menu_management(callback: CallbackQuery, db: Database):
    """Handle back to menu management"""
    categories = db.get_categories()

    menu_text = "⚙️ **Gestione Menù**\n\n"
    menu_text += "Scegli cosa vuoi fare:"

    try:
        await callback.message.edit_text(
            menu_text,
            reply_markup=AdminKeyboard.menu_management(categories)
        )
    except TelegramBadRequest:
        pass

    await callback.answer()

async def handle_cancel_add_item(callback: CallbackQuery, state: FSMContext):
    """Handle cancel add item"""
    await state.clear()

    try:
        await callback.message.edit_text(
            "❌ **Operazione Annullata**\n\n"
            "Torna alla gestione del menù.",
            reply_markup=None
        )
    except TelegramBadRequest:
        pass

    await callback.answer("❌ Operazione annullata")

async def handle_manage_categories(callback: CallbackQuery, db: Database):
    """Handle category management"""
    categories = db.get_categories()

    try:
        await callback.message.edit_text(
            "📂 **Gestione Categorie**\n\n"
            "Puoi aggiungere nuove categorie o rimuovere quelle esistenti:",
            reply_markup=AdminKeyboard.category_management(categories)
        )
    except TelegramBadRequest:
        pass

    await callback.answer()

async def handle_remove_category_confirm(callback: CallbackQuery, db: Database):
    """Handle remove category confirmation"""
    category = callback.data.split(":")[-1]

    # Check if category has items
    items = db.get_category_items(category)
    if items:
        await callback.answer(
            f"❌ Impossibile rimuovere '{category}': contiene {len(items)} piatti!",
            show_alert=True
        )
        return

    # Remove category
    if category in db.menu_data.get("categories", {}):
        del db.menu_data["categories"][category]
        db.save_menu()

    await callback.answer(f"🗑️ Categoria '{category}' rimossa!", show_alert=True)

    # Refresh category management view
    await handle_manage_categories(callback, db)

async def cmd_add_admin(message: Message, db: Database, state: FSMContext):
    """Add new admin - super admin only"""
    if not is_admin(message.from_user.id, db):
        await message.answer("❌ Non hai i permessi per questo comando!")
        return

    await message.answer(
        "👤 **Aggiungi Nuovo Admin**\n\n"
        "Invia l'ID Telegram dell'utente da rendere admin:",
        reply_markup=AdminKeyboard.cancel_add_item()
    )
    await state.set_state(AdminStates.waiting_for_admin_id)

async def handle_admin_id_input(message: Message, state: FSMContext, db: Database):
    """Handle admin ID input"""
    try:
        admin_id = int(message.text.strip())

        if db.add_admin(admin_id):
            await message.answer(
                f"✅ **Admin Aggiunto!**\n\n"
                f"🆔 ID: `{admin_id}`\n"
                f"👤 L'utente ora ha i permessi di admin."
            )
        else:
            await message.answer(
                f"⚠️ L'utente con ID `{admin_id}` è già admin!"
            )

        await state.clear()

    except ValueError:
        await message.answer(
            "❌ ID non valido! Inserisci solo numeri.",
            reply_markup=AdminKeyboard.cancel_add_item()
        )

async def cmd_add_category(message: Message, db: Database, state: FSMContext):
    """Add new category - admin only"""
    if not is_admin(message.from_user.id, db):
        await message.answer("❌ Non hai i permessi per questo comando!")
        return

    await message.answer(
        "📂 **Aggiungi Nuova Categoria**\n\n"
        "Scrivi il nome della nuova categoria del menu:",
        reply_markup=AdminKeyboard.cancel_add_item()
    )
    await state.set_state(AdminStates.waiting_for_category_name)

async def handle_category_name_input(message: Message, state: FSMContext, db: Database):
    """Handle category name input"""
    category_name = message.text.strip()

    # Add category to menu
    if db.add_category(category_name):
        await message.answer(
            f"✅ **Categoria Aggiunta!**\n\n"
            f"📂 Nome: {category_name}\n"
            f"Ora puoi aggiungere piatti a questa categoria."
        )
    else:
        await message.answer(
            f"⚠️ La categoria '{category_name}' esiste già!"
        )

    await state.clear()

async def cmd_setup_sponsor_channel(message: Message, db: Database, state: FSMContext):
    """Setup sponsor channel - admin only"""
    if not is_admin(message.from_user.id, db):
        await message.answer("❌ Non hai i permessi per questo comando!")
        return

    await message.answer(
        "📢 **Configura Canale Sponsor**\n\n"
        "Inoltra un messaggio dal canale dove vuoi che vengano pubblicati gli sponsor approvati, oppure invia l'ID del canale:"
    )
    await state.set_state(AdminStates.waiting_for_sponsor_channel)

async def handle_sponsor_channel_input(message: Message, state: FSMContext, db: Database):
    """Handle sponsor channel input"""
    if message.forward_from_chat:
        # Forwarded message from channel
        channel_id = message.forward_from_chat.id
        channel_title = message.forward_from_chat.title

        db.set_sponsor_channel_id(channel_id)
        await message.answer(
            f"✅ **Canale Sponsor Configurato!**\n\n"
            f"📢 Canale: {channel_title}\n"
            f"🆔 ID: `{channel_id}`\n\n"
            f"Gli sponsor approvati verranno ora pubblicati automaticamente in questo canale."
        )
    else:
        try:
            # Manual ID input
            channel_id = int(message.text.strip())
            db.set_sponsor_channel_id(channel_id)
            await message.answer(
                f"✅ **Canale Sponsor Configurato!**\n\n"
                f"🆔 ID: `{channel_id}`\n\n"
                f"Gli sponsor approvati verranno ora pubblicati automaticamente in questo canale."
            )
        except ValueError:
            await message.answer(
                "❌ ID non valido! Invia l'ID del canale o inoltra un messaggio dal canale."
            )
            return

    await state.clear()

async def cmd_remove_category(message: Message, db: Database):
    """Remove menu category command"""
    if message.from_user.id not in ADMIN_IDS and not db.is_admin(message.from_user.id):
        await message.answer("❌ Non hai i permessi per usare questo comando!")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Uso: /remove_category <nome_categoria>")
        return

    category_name = args[1]
    categories = db.get_categories()

    if category_name not in categories:
        await message.answer(f"❌ Categoria '{category_name}' non trovata!")
        return

    # Remove category from menu data
    del db.menu_data["categories"][category_name]
    db.save_menu()

    await message.answer(f"✅ Categoria '{category_name}' rimossa con successo!")

async def cmd_remove_item(message: Message, db: Database):
    """Remove menu item command"""
    if message.from_user.id not in ADMIN_IDS and not db.is_admin(message.from_user.id):
        await message.answer("❌ Non hai i permessi per usare questo comando!")
        return

    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("❌ Uso: /remove_item <categoria> <nome_item>")
        return

    category = args[1]
    item_name = args[2]

    if category not in db.get_categories():
        await message.answer(f"❌ Categoria '{category}' non trovata!")
        return

    items = db.get_category_items(category)
    if item_name not in items:
        await message.answer(f"❌ Item '{item_name}' non trovato nella categoria '{category}'!")
        return

    db.remove_menu_item(category, item_name)
    await message.answer(f"✅ Item '{item_name}' rimosso dalla categoria '{category}'!")

async def cmd_edit_item(message: Message, db: Database):
    """Edit menu item command"""
    if message.from_user.id not in ADMIN_IDS and not db.is_admin(message.from_user.id):
        await message.answer("❌ Non hai i permessi per usare questo comando!")
        return

    args = message.text.split(maxsplit=4)
    if len(args) < 5:
        await message.answer("❌ Uso: /edit_item <categoria> <nome_item> <nuovo_prezzo> <nuova_descrizione>")
        return

    category = args[1]
    item_name = args[2]
    try:
        new_price = int(args[3])
    except ValueError:
        await message.answer("❌ Il prezzo deve essere un numero!")
        return
    new_description = args[4]

    if category not in db.get_categories():
        await message.answer(f"❌ Categoria '{category}' non trovata!")
        return

    items = db.get_category_items(category)
    if item_name not in items:
        await message.answer(f"❌ Item '{item_name}' non trovato nella categoria '{category}'!")
        return

    # Update item
    db.menu_data["categories"][category][item_name] = {
        "price": new_price,
        "description": new_description
    }
    db.save_menu()

    await message.answer(f"✅ Item '{item_name}' aggiornato!\n💰 Prezzo: {new_price}€\n📝 Descrizione: {new_description}")

async def handle_add_category_selection(callback: CallbackQuery, state: FSMContext, db: Database):
    """Handle category selection for adding item"""
    category = callback.data.split(":")[-1]
    await state.update_data(selected_category=category)
    await state.set_state(AdminStates.waiting_for_item_name)

    try:
        await callback.message.edit_text(
            f"➕ **Aggiungi piatto alla categoria: {category}**\n\n"
            f"📝 Inserisci il nome del piatto:",
            reply_markup=AdminKeyboard.cancel_add_item()
        )
    except TelegramBadRequest:
        pass

    await callback.answer()

async def handle_item_name_input(message: Message, state: FSMContext, db: Database):
    """Handle item name input"""
    await state.update_data(item_name=message.text)
    await state.set_state(AdminStates.waiting_for_item_price)

    await message.answer(
        f"💰 **Nome piatto:** `{message.text}`\n\n"
        f"Inserisci il prezzo (solo numero, es: 8):",
        reply_markup=AdminKeyboard.cancel_add_item()
    )

async def handle_item_price_input(message: Message, state: FSMContext, db: Database):
    """Handle item price input"""
    try:
        price = int(message.text)
        await state.update_data(item_price=price)
        await state.set_state(AdminStates.waiting_for_item_description)

        data = await state.get_data()
        await message.answer(
            f"📝 **Nome:** `{data['item_name']}`\n"
            f"💰 **Prezzo:** `{price}€`\n\n"
            f"Inserisci la descrizione del piatto:",
            reply_markup=AdminKeyboard.cancel_add_item()
        )
    except ValueError:
        await message.answer(
            "❌ **Prezzo non valido!**\n\n"
            "Inserisci solo un numero (es: 8):",
            reply_markup=AdminKeyboard.cancel_add_item()
        )

async def handle_item_description_input(message: Message, state: FSMContext, db: Database):
    """Handle item description input"""
    data = await state.get_data()

    # Add item to database
    success = db.add_menu_item(
        category=data['selected_category'],
        name=data['item_name'],
        price=data['item_price'],
        description=message.text
    )

    await state.clear()

    if success:
        await message.answer(
            f"✅ **Piatto aggiunto con successo!**\n\n"
            f"📝 **Nome:** `{data['item_name']}`\n"
            f"💰 **Prezzo:** `{data['item_price']}€`\n"
            f"📂 **Categoria:** `{data['selected_category']}`\n"
            f"📄 **Descrizione:** `{message.text}`"
        )
    else:
        await message.answer(
            "❌ **Errore nell'aggiunta del piatto!**\n\n"
            "Il piatto potrebbe già esistere."
        )

async def handle_remove_item(callback: CallbackQuery, db: Database):
    """Handle item removal"""
    parts = callback.data.split(":")
    category = parts[1]
    item_name = parts[2]

    success = db.remove_menu_item(category, item_name)

    if success:
        await callback.answer(f"✅ {item_name} rimosso!", show_alert=True)

        # Update the view
        items = db.get_category_items(category)
        item_names = list(items.keys()) if items else []

        try:
            await callback.message.edit_text(
                f"📋 **Gestione: {category}**\n\n"
                f"Gestisci i piatti di questa categoria:",
                reply_markup=AdminKeyboard.category_items_management(category, item_names)
            )
        except TelegramBadRequest:
            pass
    else:
        await callback.answer("❌ Errore nella rimozione!", show_alert=True)

async def handle_edit_item_selection(callback: CallbackQuery, state: FSMContext, db: Database):
    """Handle edit item selection"""
    parts = callback.data.split(":")
    category = parts[1]
    item_name = parts[2]

    items = db.get_category_items(category)
    item_data = items.get(item_name, {})

    await state.update_data(
        edit_category=category,
        edit_item_name=item_name,
        current_price=item_data.get('price', 0),
        current_description=item_data.get('description', '')
    )
    await state.set_state(AdminStates.waiting_for_edit_price)

    try:
        await callback.message.edit_text(
            f"✏️ **Modifica: {item_name}**\n\n"
            f"📂 **Categoria:** `{category}`\n"
            f"💰 **Prezzo attuale:** `{item_data.get('price', 0)}€`\n"
            f"📝 **Descrizione attuale:** `{item_data.get('description', 'Nessuna descrizione')}`\n\n"
            f"Inserisci il nuovo prezzo (solo numero):",
            reply_markup=AdminKeyboard.cancel_add_item()
        )
    except TelegramBadRequest:
        pass

    await callback.answer()

async def handle_edit_price_input(message: Message, state: FSMContext, db: Database):
    """Handle edit price input"""
    try:
        new_price = int(message.text.strip())
        await state.update_data(new_price=new_price)
        await state.set_state(AdminStates.waiting_for_edit_description)

        data = await state.get_data()
        await message.answer(
            f"✏️ **Modifica: {data['edit_item_name']}**\n\n"
            f"💰 **Nuovo prezzo:** `{new_price}€`\n\n"
            f"Inserisci la nuova descrizione:",
            reply_markup=AdminKeyboard.cancel_add_item()
        )
    except ValueError:
        await message.answer(
            "❌ **Prezzo non valido!**\n\n"
            "Inserisci solo un numero (es: 8):",
            reply_markup=AdminKeyboard.cancel_add_item()
        )

async def handle_edit_description_input(message: Message, state: FSMContext, db: Database):
    """Handle edit description input"""
    data = await state.get_data()
    new_description = message.text.strip()

    # Update item in database
    if data['edit_category'] not in db.menu_data.get("categories", {}):
        await message.answer("❌ **Errore:** Categoria non trovata!")
        await state.clear()
        return

    if data['edit_item_name'] not in db.menu_data["categories"][data['edit_category']]:
        await message.answer("❌ **Errore:** Piatto non trovato!")
        await state.clear()
        return

    # Update the item
    db.menu_data["categories"][data['edit_category']][data['edit_item_name']] = {
        "price": data['new_price'],
        "description": new_description
    }
    db.save_menu()

    await state.clear()

    await message.answer(
        f"✅ **Piatto modificato con successo!**\n\n"
        f"📝 **Nome:** `{data['edit_item_name']}`\n"
        f"💰 **Nuovo prezzo:** `{data['new_price']}€`\n"
        f"📂 **Categoria:** `{data['edit_category']}`\n"
        f"📄 **Nuova descrizione:** `{new_description}`"
    )

async def handle_add_to_specific_category(callback: CallbackQuery, state: FSMContext, db: Database):
    """Handle adding item to specific category"""
    category = callback.data.split(":")[-1]
    await state.update_data(selected_category=category)
    await state.set_state(AdminStates.waiting_for_item_name)

    try:
        await callback.message.edit_text(
            f"➕ **Aggiungi piatto a: {category}**\n\n"
            f"📝 Inserisci il nome del piatto:",
            reply_markup=AdminKeyboard.cancel_add_item()
        )
    except TelegramBadRequest:
        pass

    await callback.answer()

async def handle_remove_category(callback: CallbackQuery, db: Database):
    """Handle category removal"""
    category = callback.data.split(":")[-1]

    success = db.remove_category(category)

    if success:
        await callback.answer(f"✅ Categoria {category} rimossa!", show_alert=True)

        # Update view
        categories = db.get_categories()
        try:
            await callback.message.edit_text(
                "📂 **Gestione Categorie**\n\n"
                "Seleziona un'azione:",
                reply_markup=AdminKeyboard.category_management(categories)
            )
        except TelegramBadRequest:
            pass
    else:
        await callback.answer("❌ Errore nella rimozione!", show_alert=True)

async def handle_add_new_category(callback: CallbackQuery, state: FSMContext, db: Database):
    """Handle add new category"""
    await state.set_state(AdminStates.waiting_for_new_category)

    try:
        await callback.message.edit_text(
            "➕ **Aggiungi Nuova Categoria**\n\n"
            "📝 Inserisci il nome della nuova categoria:",
            reply_markup=AdminKeyboard.cancel_add_item()
        )
    except TelegramBadRequest:
        pass

    await callback.answer()

async def handle_new_category_input(message: Message, state: FSMContext, db: Database):
    """Handle new category name input"""
    category_name = message.text.strip()

    success = db.add_category(category_name)
    await state.clear()

    if success:
        await message.answer(
            f"✅ **Categoria aggiunta!**\n\n"
            f"📂 **Nome:** `{category_name}`"
        )
    else:
        await message.answer(
            f"❌ **Errore!**\n\n"
            f"La categoria `{category_name}` già esiste."
        )

def register_handlers(dp, db: Database, bot: Bot):
    """Register admin handlers"""

    @dp.message(Command("setup_staff"))
    async def setup_staff_handler(message: Message):
        await cmd_setup_staff(message, db)

    @dp.message(Command("create_topics"))
    async def create_topics_handler(message: Message):
        await cmd_create_topics(message, db, bot)

    @dp.message(Command("gestisci_menu"))
    async def gestisci_menu_handler(message: Message):
        await cmd_gestisci_menu(message, db)

    @dp.message(Command("aggiungi_piatto"))
    async def aggiungi_piatto_handler(message: Message, state: FSMContext):
        await cmd_aggiungi_piatto(message, db, state)

    @dp.message(Command("add_admin"))
    async def add_admin_handler(message: Message, state: FSMContext):
        await cmd_add_admin(message, db, state)

    @dp.message(Command("add_category"))
    async def add_category_handler(message: Message, state: FSMContext):
        await cmd_add_category(message, db, state)

    @dp.message(Command("setup_sponsor_channel"))
    async def setup_sponsor_channel_handler(message: Message, state: FSMContext):
        await cmd_setup_sponsor_channel(message, db, state)

    @dp.message(Command("remove_category"))
    async def remove_category_handler(message: Message):
        await cmd_remove_category(message, db)

    @dp.message(Command("remove_item"))
    async def remove_item_handler(message: Message):
        await cmd_remove_item(message, db)

    @dp.message(Command("edit_item"))
    async def edit_item_handler(message: Message):
        await cmd_edit_item(message, db)

    @dp.callback_query(lambda c: c.data.startswith("add_category:"))
    async def category_for_new_item_handler(callback: CallbackQuery, state: FSMContext):
        await handle_category_for_new_item(callback, state)

    @dp.message(AdminStates.waiting_for_item_name)
    async def item_name_handler(message: Message, state: FSMContext):
        await handle_item_name_input(message, state)

    @dp.message(AdminStates.waiting_for_item_price)
    async def item_price_handler(message: Message, state: FSMContext):
        await handle_item_price_input(message, state)

    @dp.message(AdminStates.waiting_for_item_description)
    async def item_description_handler(message: Message, state: FSMContext):
        await handle_item_description_input(message, state, db)

    @dp.message(AdminStates.waiting_for_admin_id)
    async def admin_id_handler(message: Message, state: FSMContext):
        await handle_admin_id_input(message, state, db)

    @dp.message(AdminStates.waiting_for_category_name)
    async def category_name_handler(message: Message, state: FSMContext):
        await handle_category_name_input(message, state, db)

    @dp.message(AdminStates.waiting_for_sponsor_channel)
    async def sponsor_channel_handler(message: Message, state: FSMContext):
        await handle_sponsor_channel_input(message, state, db)

    @dp.callback_query(lambda c: c.data.startswith("view_category:"))
    async def view_category_handler(callback: CallbackQuery):
        await handle_view_category(callback, db)

    @dp.callback_query(lambda c: c.data.startswith("remove_item:"))
    async def remove_item_handler(callback: CallbackQuery):
        await handle_remove_item(callback, db)

    @dp.callback_query(lambda c: c.data == "back_to_menu_management")
    async def back_to_menu_management_handler(callback: CallbackQuery):
        await handle_back_to_menu_management(callback, db)

    @dp.callback_query(lambda c: c.data == "cancel_add_item")
    async def cancel_add_item_handler(callback: CallbackQuery, state: FSMContext):
        await handle_cancel_add_item(callback, state)

    @dp.callback_query(lambda c: c.data == "add_new_category")
    async def add_new_category_handler(callback: CallbackQuery, state: FSMContext):
        await cmd_add_category(callback.message, db, state)
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "manage_categories")
    async def manage_categories_handler(callback: CallbackQuery):
        await handle_manage_categories(callback, db)

    @dp.callback_query(lambda c: c.data.startswith("remove_category:"))
    async def remove_category_handler(callback: CallbackQuery):
        await handle_remove_category_confirm(callback, db)

    @dp.callback_query(lambda c: c.data.startswith("edit_item:"))
    async def edit_item_handler(callback: CallbackQuery, state: FSMContext):
        await handle_edit_item_selection(callback, state, db)

    @dp.callback_query(lambda c: c.data.startswith("add_to_category:"))
    async def add_to_category_handler(callback: CallbackQuery, state: FSMContext):
        await handle_add_to_specific_category(callback, state, db)

    @dp.message(AdminStates.waiting_for_edit_price)
    async def edit_price_handler(message: Message, state: FSMContext):
        await handle_edit_price_input(message, state, db)

    @dp.message(AdminStates.waiting_for_edit_description)
    async def edit_description_handler(message: Message, state: FSMContext):
        await handle_edit_description_input(message, state, db)

    @dp.callback_query(lambda c: c.data == "add_new_item")
    async def add_item_handler(callback: CallbackQuery, state: FSMContext):
        await cmd_aggiungi_piatto(callback.message, db, state)
        await callback.answer()