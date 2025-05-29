from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import logging
import os

# Admin ID Telegram (inserisci il tuo ID Telegram da admin qui)
ADMIN_IDS = [5334649049]

# Dati utente temporanei (in memoria)
utenti = {}

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌟 Seguici sul nostro canale!", url="https://t.me/MisterrShopNT")],
        [InlineKeyboardButton("🎰 Visita il Casinò", url="https://preview--lucky-emerald-casino-web.lovable.app/")],
        [InlineKeyboardButton("💎 Ricarica Saldo", callback_data='ricarica'), 
         InlineKeyboardButton("🎯 Registrati Ora", callback_data='registrati')],
        [InlineKeyboardButton("💰 Prelievo Express", callback_data='preleva'),
         InlineKeyboardButton("ℹ️ Informazioni", callback_data='info')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """🎰✨ **BENVENUTO AL MISTERSHOP CASINO** ✨🎰

🤖 Sono **Stanley**, il Robot del Casinò!
🎩 Il tuo assistente personale per:

💎 Ricariche istantanee
🏆 Registrazioni rapide  
💸 Prelievi veloci
🎲 Servizi premium

Scegli un'opzione dal menu elegante qui sotto:"""

    # Prova a inviare l'immagine, se fallisce invia solo il testo
    try:
        with open('attached_assets/stanley_robot.jpg', 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=welcome_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    except Exception as e:
        # Fallback: invia solo il messaggio di testo se l'immagine non funziona
        enhanced_welcome = f"""🤖 **STANLEY - IL ROBOT DEL CASINÒ** 🎰

{welcome_text}"""
        await update.message.reply_text(
            enhanced_welcome,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data

    if action == 'ricarica':
        keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data='back_to_home')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Inserisci il tuo nickname per iniziare la ricarica:", reply_markup=reply_markup)
        context.user_data['action'] = 'ricarica_nickname'

    elif action == 'registrati':
        keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data='back_to_home')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Inserisci un nickname per registrarti:", reply_markup=reply_markup)
        context.user_data['action'] = 'reg_nickname'

    elif action == 'preleva':
        keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data='back_to_home')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Inserisci il tuo nickname per prelevare:", reply_markup=reply_markup)
        context.user_data['action'] = 'preleva_nickname'

    elif action == 'back_to_home':
        context.user_data.clear()
        
        # Per i callback, dobbiamo inviare un nuovo messaggio invece di usare update.message
        keyboard = [
            [InlineKeyboardButton("🌟 Seguici sul nostro canale!", url="https://t.me/MisterrShopNT")],
            [InlineKeyboardButton("🎰 Visita il Casinò", url="https://preview--lucky-emerald-casino-web.lovable.app/")],
            [InlineKeyboardButton("💎 Ricarica Saldo", callback_data='ricarica'), 
             InlineKeyboardButton("🎯 Registrati Ora", callback_data='registrati')],
            [InlineKeyboardButton("💰 Prelievo Express", callback_data='preleva'),
             InlineKeyboardButton("ℹ️ Informazioni", callback_data='info')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """🎰✨ **BENVENUTO AL MISTERSHOP CASINO** ✨🎰

🤖 Sono **Stanley**, il Robot del Casinò!
🎩 Il tuo assistente personale per:

💎 Ricariche istantanee
🏆 Registrazioni rapide  
💸 Prelievi veloci
🎲 Servizi premium

Scegli un'opzione dal menu elegante qui sotto:"""

        # Prova a inviare l'immagine, se fallisce invia solo il testo
        try:
            with open('attached_assets/stanley_robot.jpg', 'rb') as photo:
                await query.message.reply_photo(
                    photo=photo,
                    caption=welcome_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        except Exception as e:
            # Fallback: invia solo il messaggio di testo se l'immagine non funziona
            enhanced_welcome = f"""🤖 **STANLEY - IL ROBOT DEL CASINÒ** 🎰

{welcome_text}"""
            await query.message.reply_text(
                enhanced_welcome,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        return

    elif action == 'info':
        info_text = """🎰✨ **MISTERSHOP CASINO** ✨🎰

🤖 **Stanley - Il Robot del Casinò**
🎩 Il tuo assistente AI personale

📋 **Servizi Disponibili:**
💎 Ricariche istantanee
🏆 Registrazione account  
💸 Prelievi Express rapidi
🔐 Sistema di sicurezza avanzato

⚡ **Caratteristiche:**
🎯 Interface moderna e intuitiva
🛡️ Protezione dati massima
🚀 Elaborazione super veloce
🎲 Esperienza casinò premium

👑 **Owner:** @Motoreasoldi
📞 **Supporto:** Per problemi contatta @Motoreasoldi

🤖 *Powered by Stanley AI Technology*"""
        keyboard = [[InlineKeyboardButton("🔙 Torna al Menu", callback_data='back_to_home')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(info_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "senza_username"
    text = update.message.text
    action = context.user_data.get('action')

    if action == 'ricarica_nickname':
        context.user_data['nickname'] = text
        keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data='back_to_home')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"✅ **Nickname confermato:** `{text}`\n\n💎 Inserisci l'importo per la ricarica:\n💰 *Importo in Euro (€)*", reply_markup=reply_markup, parse_mode='Markdown')
        context.user_data['action'] = 'ricarica_importo'

    elif action == 'ricarica_importo':
        try:
            importo = int(text)
            if importo <= 0:
                keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data='back_to_home')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("❌ L'importo deve essere maggiore di 0. Riprova:", reply_markup=reply_markup)
                return
            context.user_data['importo_ricarica'] = importo
            nickname = context.user_data.get('nickname')
            keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data='back_to_home')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"✅ **Importo confermato:** `{importo}€`\n\n📸 **Passo finale:**\nInvia uno screenshot del pagamento\n\n🔐 **Stanley verificherà tutto per te!**\n⚡ Processo di approvazione rapido", reply_markup=reply_markup, parse_mode='Markdown')
            context.user_data['action'] = 'ricarica_attesa_foto'
        except ValueError:
            keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data='back_to_home')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("❌ Inserisci un numero valido. Esempio: 50", reply_markup=reply_markup)

    elif action == 'reg_nickname':
        context.user_data['nickname'] = text
        keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data='back_to_home')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"🎯 **Nickname selezionato:** `{text}`\n\n🔐 **Crea la tua password:**\n🛡️ *Scegli una password sicura e memorabile*", reply_markup=reply_markup, parse_mode='Markdown')
        context.user_data['action'] = 'reg_password'

    elif action == 'reg_password':
        nickname = context.user_data.get('nickname')
        password = text
        
        # Salva temporaneamente i dati per l'approvazione
        context.user_data['pending_registration'] = {
            'user_id': user_id,
            'nickname': nickname,
            'password': password,
            'username': username,
            'first_name': update.message.from_user.first_name or "N/A",
            'last_name': update.message.from_user.last_name or ""
        }
        
        # Invia richiesta di registrazione all'admin per approvazione
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"📝 NUOVA REGISTRAZIONE DA APPROVARE:\n\n"
                     f"👤 Nickname: {nickname}\n"
                     f"🆔 ID Telegram: {user_id}\n"
                     f"📱 Username: @{username}\n"
                     f"🔐 Password: {password}\n\n"
                     f"Vuoi approvare questa registrazione?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Approva Registrazione", callback_data=f"approva_reg_{user_id}_{nickname}")],
                    [InlineKeyboardButton("❌ Rifiuta Registrazione", callback_data=f"rifiuta_reg_{user_id}")]
                ])
            )
        await update.message.reply_text("🎩 **Registrazione inviata!**\n\n⚡ Stanley sta processando la tua richiesta...\n🏆 Riceverai conferma a breve!", parse_mode='Markdown')
        context.user_data.clear()

    elif action == 'preleva_nickname':
        context.user_data['nickname'] = text
        keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data='back_to_home')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"💸 **Account identificato:** `{text}`\n\n💎 **Prelievo Express:**\nInserisci l'importo da prelevare\n💰 *Importo in Euro (€)*", reply_markup=reply_markup, parse_mode='Markdown')
        context.user_data['action'] = 'preleva_importo'

    elif action == 'custom_reg_message':
        user_id = context.user_data.get('target_user_id')
        nickname = context.user_data.get('target_nickname')
        custom_message = text
        
        full_message = f"🏆 **REGISTRAZIONE COMPLETATA!**\n\n📝 **Messaggio dall'Admin:**\n{custom_message}\n\n🎯 **Nickname:** `{nickname}`\n💎 **Saldo iniziale:** `0€`\n\n🤖 *Benvenuto nel MisterShop Casino!*"
        
        await context.bot.send_message(chat_id=user_id, text=full_message, parse_mode='Markdown')
        await update.message.reply_text(f"✅ Messaggio personalizzato inviato a {nickname}")
        context.user_data.clear()
        return

    elif action == 'custom_ricarica_message':
        user_id = context.user_data.get('target_user_id')
        importo = context.user_data.get('target_importo')
        nickname = context.user_data.get('target_nickname')
        custom_message = text
        
        full_message = f"🎉 **RICARICA APPROVATA!**\n\n📝 **Messaggio dall'Admin:**\n{custom_message}\n\n💎 **Importo ricaricato:** `{importo}€`\n👤 **Account:** `{nickname}`\n\n🤖 *Stanley ha completato la transazione*"
        
        await context.bot.send_message(chat_id=user_id, text=full_message, parse_mode='Markdown')
        await update.message.reply_text(f"✅ Messaggio personalizzato inviato per ricarica di {importo}€")
        context.user_data.clear()
        return

    elif action == 'custom_prelievo_message':
        user_id = context.user_data.get('target_user_id')
        importo = context.user_data.get('target_importo')
        nickname = context.user_data.get('target_nickname')
        custom_message = text
        
        full_message = f"💸 **PRELIEVO EXPRESS APPROVATO!**\n\n📝 **Messaggio dall'Admin:**\n{custom_message}\n\n💰 **Importo:** `{importo}€`\n👤 **Account:** `{nickname}`\n\n🤖 *Stanley ha verificato tutto*"
        
        await context.bot.send_message(chat_id=user_id, text=full_message, parse_mode='Markdown')
        await update.message.reply_text(f"✅ Messaggio personalizzato inviato per prelievo di {importo}€")
        context.user_data.clear()
        return

    elif action == 'preleva_importo':
        try:
            importo = int(text)
            if importo <= 0:
                keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data='back_to_home')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("❌ L'importo deve essere maggiore di 0. Riprova:", reply_markup=reply_markup)
                return

            context.user_data['importo_prelievo'] = importo
            nickname = context.user_data.get('nickname')
            # No saldo check
            for admin_id in ADMIN_IDS:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"💸 RICHIESTA PRELIEVO DA APPROVARE:\n\n"
                         f"👤 Nickname: {nickname}\n"
                         f"🆔 ID Telegram: {update.message.from_user.id}\n"
                         f"📱 Username: @{username}\n"
                         f"💰 Importo richiesto: {importo}€\n\n"
                         f"Vuoi approvare questo prelievo?",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✅ Approva Prelievo", callback_data=f"approva_prelievo_{update.message.from_user.id}_{importo}_{nickname}")],
                        [InlineKeyboardButton("❌ Rifiuta Prelievo", callback_data=f"rifiuta_prelievo_{update.message.from_user.id}")]
                    ])
                )
            await update.message.reply_text("💸 **Richiesta Prelievo Express inviata!**\n\n🎩 Stanley sta verificando il tuo saldo...\n⚡ Elaborazione rapida in corso!", parse_mode='Markdown')
            context.user_data.clear()

        except ValueError:
            keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data='back_to_home')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("❌ Inserisci un numero valido. Esempio: 50", reply_markup=reply_markup)

    else:
        # Se l'utente scrive senza essere in nessuna procedura
        await update.message.reply_text("🎩 Ciao! Sono **Stanley**, il Robot del Casinò!\n\n🎰 Usa il comando /start per accedere al menu principale.", parse_mode='Markdown')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    action = context.user_data.get('action')
    if action == 'ricarica_attesa_foto':
        nickname = context.user_data.get('nickname', 'sconosciuto')
        importo = context.user_data.get('importo_ricarica', 0)
        username = update.message.from_user.username or "senza_username"
        photo = update.message.photo[-1]
        file_id = photo.file_id

        for admin_id in ADMIN_IDS:
            await context.bot.send_photo(chat_id=admin_id, photo=file_id,
                                         caption=f"📥 RICHIESTA RICARICA DA APPROVARE:\n\n"
                                                f"👤 Nickname: {nickname}\n"
                                                f"🆔 ID Telegram: {update.message.from_user.id}\n"
                                                f"📱 Username: @{username}\n"
                                                f"💰 Importo richiesto: {importo}€\n\n"
                                                f"Vuoi approvare questa ricarica?",
                                         reply_markup=InlineKeyboardMarkup([
                                             [InlineKeyboardButton("✅ Approva Ricarica", callback_data=f"conferma_{update.message.from_user.id}_{importo}_{nickname}")],
                                             [InlineKeyboardButton("❌ Rifiuta Ricarica", callback_data=f"rifiuta_ricarica_{update.message.from_user.id}")]
                                         ]))
        await update.message.reply_text("📸 **Screenshot ricevuto!**\n\n🎩 Stanley sta analizzando il pagamento...\n⚡ Verifica rapida in corso\n🔐 Processo sicuro al 100%", parse_mode='Markdown')
        context.user_data.clear()

async def handle_admin_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if query.from_user.id not in ADMIN_IDS:
        await query.answer("⛔ Non autorizzato")
        return

    if data.startswith("conferma_"):
        parts = data.split("_")
        user_id = int(parts[1])
        importo = int(parts[2]) if len(parts) > 2 else 100
        nickname = parts[3] if len(parts) > 3 else "sconosciuto"

        # Opzioni per messaggio personalizzato
        keyboard = [
            [InlineKeyboardButton("✅ Invia Approvazione Standard", callback_data=f"send_standard_ricarica_{user_id}_{importo}_{nickname}")],
            [InlineKeyboardButton("📝 Invia con Messaggio Personalizzato", callback_data=f"send_custom_ricarica_{user_id}_{importo}_{nickname}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_caption(
            caption=f"✅ RICARICA APPROVATA: {importo}€ per {nickname}\n\nScegli come notificare l'utente:",
            reply_markup=reply_markup
        )

    elif data.startswith("rifiuta_ricarica_"):
        user_id = int(data.split("_")[2])
        await query.message.reply_text("📝 Inserisci la motivazione del rifiuto:")
        context.user_data['admin_action'] = 'motivazione_rifiuto_ricarica'
        context.user_data['rifiuto_user_id'] = user_id
        context.user_data['original_message_id'] = query.message.message_id
        await query.answer("Inserisci motivazione")

    elif data.startswith("approva_reg_"):
        parts = data.split("_", 3)
        user_id = int(parts[2])
        nickname = parts[3]
        
        # Ottieni informazioni complete dell'utente
        try:
            user_obj = await context.bot.get_chat(user_id)
            first_name = user_obj.first_name or "N/A"
            last_name = user_obj.last_name or ""
            username = user_obj.username or "senza_username"
        except:
            first_name = "N/A"
            last_name = ""
            username = "senza_username"

        # Registra realmente l'utente
        from datetime import datetime
        utenti[user_id] = {
            'nickname': nickname,
            'telegram_id': user_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'saldo': 0,
            'registration_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'attivo'
        }

        # Opzioni per messaggio personalizzato
        keyboard = [
            [InlineKeyboardButton("✅ Invia Approvazione Standard", callback_data=f"send_standard_reg_{user_id}_{nickname}")],
            [InlineKeyboardButton("📝 Invia con Messaggio Personalizzato", callback_data=f"send_custom_reg_{user_id}_{nickname}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=f"✅ REGISTRAZIONE APPROVATA per {nickname}\n\n👤 Utente registrato con successo!\n🆔 ID: {user_id}\n📱 Username: @{username}\n\nScegli come notificare l'utente:",
            reply_markup=reply_markup
        )

    elif data.startswith("approva_prelievo_"):
        parts = data.split("_")
        user_id = int(parts[2])
        importo = int(parts[3])
        nickname = parts[4]

        # Opzioni per messaggio personalizzato
        keyboard = [
            [InlineKeyboardButton("✅ Invia Approvazione Standard", callback_data=f"send_standard_prelievo_{user_id}_{importo}_{nickname}")],
            [InlineKeyboardButton("📝 Invia con Messaggio Personalizzato", callback_data=f"send_custom_prelievo_{user_id}_{importo}_{nickname}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=f"✅ PRELIEVO APPROVATO: {importo}€ per {nickname}\n\nScegli come notificare l'utente:",
            reply_markup=reply_markup
        )

    elif data.startswith("rifiuta_reg_"):
        user_id = int(data.split("_")[2])
        await query.message.reply_text("📝 Inserisci la motivazione del rifiuto:")
        context.user_data['admin_action'] = 'motivazione_rifiuto_reg'
        context.user_data['rifiuto_user_id'] = user_id
        context.user_data['original_message_id'] = query.message.message_id
        await query.answer("Inserisci motivazione")

    elif data.startswith("rifiuta_prelievo_"):
        user_id = int(data.split("_")[2])
        await query.message.reply_text("📝 Inserisci la motivazione del rifiuto:")
        context.user_data['admin_action'] = 'motivazione_rifiuto_prelievo'
        context.user_data['rifiuto_user_id'] = user_id
        context.user_data['original_message_id'] = query.message.message_id
        await query.answer("Inserisci motivazione")

    # Handlers per messaggi standard
    elif data.startswith("send_standard_reg_"):
        parts = data.split("_", 4)
        user_id = int(parts[3])
        nickname = parts[4]
        
        await context.bot.send_message(
            chat_id=user_id, 
            text=f"🏆 **REGISTRAZIONE COMPLETATA!**\n\n🎯 **Nickname:** `{nickname}`\n💎 **Saldo iniziale:** `0€`\n🎩 **Status:** ✨ **Membro Registrato** ✨\n\n🚀 **Benvenuto nel MisterShop Casino!**\n🤖 *Stanley ti accompagnerà in questa avventura*",
            parse_mode='Markdown'
        )
        await query.edit_message_text(f"✅ Notifica standard inviata a {nickname}")

    elif data.startswith("send_custom_reg_"):
        parts = data.split("_", 4)
        user_id = int(parts[3])
        nickname = parts[4]
        
        await query.message.reply_text(f"📝 **Scrivi il messaggio personalizzato per {nickname}:**")
        context.user_data['admin_action'] = 'custom_reg_message'
        context.user_data['target_user_id'] = user_id
        context.user_data['target_nickname'] = nickname
        await query.answer("Scrivi messaggio personalizzato")

    elif data.startswith("send_standard_ricarica_"):
        parts = data.split("_")
        user_id = int(parts[3])
        importo = int(parts[4])
        nickname = parts[5]
        
        await context.bot.send_message(
            chat_id=user_id, 
            text=f"🎉 **RICARICA APPROVATA!**\n\n💎 **Importo ricaricato:** `{importo}€`\n👤 **Account:** `{nickname}`\n\n🎰 **Benvenuto nel casinò!**\n🤖 *Stanley ha completato la transazione*",
            parse_mode='Markdown'
        )
        await query.edit_message_text(f"✅ Notifica standard inviata per ricarica di {importo}€")

    elif data.startswith("send_custom_ricarica_"):
        parts = data.split("_")
        user_id = int(parts[3])
        importo = int(parts[4])
        nickname = parts[5]
        
        await query.message.reply_text(f"📝 **Scrivi il messaggio personalizzato per la ricarica di {importo}€ a {nickname}:**")
        context.user_data['admin_action'] = 'custom_ricarica_message'
        context.user_data['target_user_id'] = user_id
        context.user_data['target_importo'] = importo
        context.user_data['target_nickname'] = nickname
        await query.answer("Scrivi messaggio personalizzato")

    elif data.startswith("send_standard_prelievo_"):
        parts = data.split("_")
        user_id = int(parts[3])
        importo = int(parts[4])
        nickname = parts[5]
        
        await context.bot.send_message(
            chat_id=user_id,
            text=f"💸 **PRELIEVO EXPRESS APPROVATO!**\n\n💰 **Importo:** `{importo}€`\n👤 **Account:** `{nickname}`\n\n⚡ **Elaborazione in corso...**\n🏦 **Pagamento entro 24h**\n🤖 *Stanley ha verificato tutto*",
            parse_mode='Markdown'
        )
        await query.edit_message_text(f"✅ Notifica standard inviata per prelievo di {importo}€")

    elif data.startswith("send_custom_prelievo_"):
        parts = data.split("_")
        user_id = int(parts[3])
        importo = int(parts[4])
        nickname = parts[5]
        
        await query.message.reply_text(f"📝 **Scrivi il messaggio personalizzato per il prelievo di {importo}€ a {nickname}:**")
        context.user_data['admin_action'] = 'custom_prelievo_message'
        context.user_data['target_user_id'] = user_id
        context.user_data['target_importo'] = importo
        context.user_data['target_nickname'] = nickname
        await query.answer("Scrivi messaggio personalizzato")

async def handle_combined_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Prima controlla se è un'azione admin
    if update.effective_user.id in ADMIN_IDS:
        # Importa qui per evitare circular import
        action = context.user_data.get('admin_action')
        if action and action in ['send_global_announcement', 'motivazione_rifiuto_ricarica', 'motivazione_rifiuto_reg', 'motivazione_rifiuto_prelievo', 'cerca_utente', 'elimina_utente', 'aggiungi_admin', 'rimuovi_admin', 'edit_saldo', 'send_msg_to_user']:
            from admin_panel_handlers import admin_handle_text
            await admin_handle_text(update, context)
            return
        else:
            # Se admin ma non in modalità admin specifica, gestisci come utente normale
            await handle_text(update, context)
    else:
        # Altrimenti gestisci come utente normale
        await handle_text(update, context)

if __name__ == '__main__':
    from admin_panel_handlers import admin_panel, admin_message_action, admin_handle_text

    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("❌ BOT_TOKEN non trovato nelle variabili d'ambiente!")
        exit(1)
    
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(handle_menu, pattern="^(ricarica|registrati|preleva|info|back_to_home)$"))
    app.add_handler(CallbackQueryHandler(handle_admin_confirm, pattern="^(conferma_|approva_reg_|approva_prelievo_|rifiuta_ricarica_|rifiuta_reg_|rifiuta_prelievo_|send_standard_|send_custom_)"))
    app.add_handler(CallbackQueryHandler(admin_message_action, pattern="^(msg_admin|gestione_utenti|gestione_admin|lista_utenti|lista_admin|cerca_utente|elimina_utente|aggiungi_admin|rimuovi_admin|reset_sistema|conferma_reset|annulla_reset|user_page_|user_info_|edit_saldo_|delete_user_|confirm_delete_|msg_user_|back_to_admin)"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_combined_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("🤖 Stanley Bot avviato correttamente!")
    print("✅ Tutti gli handler registrati")
    print("🔄 Avvio polling...")
    
    try:
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"❌ Errore durante l'esecuzione: {e}")
        exit(1)