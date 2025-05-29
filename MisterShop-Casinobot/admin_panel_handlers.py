from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

ADMIN_IDS = [5334649049]

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Accesso negato.")
        return

    keyboard = [
        [InlineKeyboardButton("👥 Gestione Utenti", callback_data="gestione_utenti")],
        [InlineKeyboardButton("🔧 Gestione Admin", callback_data="gestione_admin")],
        [InlineKeyboardButton("📢 Invia Annuncio Globale", callback_data="msg_admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔐 Pannello Admin Avanzato", reply_markup=reply_markup)

async def admin_message_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "msg_admin":
        keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data="back_to_admin")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("📢 **ANNUNCIO GLOBALE**\n\nScrivi il messaggio da inviare a tutti gli utenti registrati:", reply_markup=reply_markup)
        context.user_data['admin_action'] = 'send_global_announcement'

    elif query.data == "back_to_admin":
        context.user_data.clear()
        
        # Per i callback admin, inviamo direttamente il pannello admin
        if update.effective_user.id not in ADMIN_IDS:
            await query.answer("⛔ Accesso negato.")
            return

        keyboard = [
            [InlineKeyboardButton("👥 Gestione Utenti", callback_data="gestione_utenti")],
            [InlineKeyboardButton("🔧 Gestione Admin", callback_data="gestione_admin")],
            [InlineKeyboardButton("📢 Invia Annuncio Globale", callback_data="msg_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("🔐 Pannello Admin Avanzato", reply_markup=reply_markup)
        return

    elif query.data == "gestione_utenti":
        from main import utenti
        keyboard = [
            [InlineKeyboardButton("📋 Lista Utenti Registrati", callback_data="lista_utenti")],
            [InlineKeyboardButton("🔍 Cerca Utente", callback_data="cerca_utente")],
            [InlineKeyboardButton("🗑️ Elimina Utente", callback_data="elimina_utente")],
            [InlineKeyboardButton("🔙 Torna al Menu Admin", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("👥 Gestione Utenti - Scegli un'opzione:", reply_markup=reply_markup)

    elif query.data == "gestione_admin":
        keyboard = [
            [InlineKeyboardButton("📋 Lista Admin", callback_data="lista_admin")],
            [InlineKeyboardButton("➕ Aggiungi Admin", callback_data="aggiungi_admin")],
            [InlineKeyboardButton("➖ Rimuovi Admin", callback_data="rimuovi_admin")],
            [InlineKeyboardButton("🔄 Reset Sistema", callback_data="reset_sistema")],
            [InlineKeyboardButton("🔙 Torna al Menu Admin", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("🔧 Gestione Admin - Scegli un'opzione:", reply_markup=reply_markup)

    elif query.data == "lista_utenti":
        from main import utenti
        if not utenti:
            await query.message.reply_text("📭 Nessun utente registrato al momento.")
        else:
            # Mostra la prima pagina (utenti 0-9)
            await show_users_page(query, context, 0)
    
    elif query.data.startswith("user_page_"):
        page_num = int(query.data.split("_")[2])
        await show_users_page(query, context, page_num)
    
    elif query.data.startswith("user_info_"):
        user_id = int(query.data.split("_")[2])
        await show_user_details(query, context, user_id)

    elif query.data == "lista_admin":
        lista = "🔧 ADMIN ATTIVI:\n\n"
        for admin_id in ADMIN_IDS:
            lista += f"🆔 Admin ID: {admin_id}\n"
        keyboard = [[InlineKeyboardButton("🔙 Torna alla Gestione Admin", callback_data="gestione_admin")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(lista, reply_markup=reply_markup)

    

    elif query.data == "cerca_utente":
        keyboard = [[InlineKeyboardButton("🔙 Torna alla Gestione Utenti", callback_data="gestione_utenti")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("🔍 Inserisci l'ID utente da cercare:", reply_markup=reply_markup)
        context.user_data['admin_action'] = 'cerca_utente'

    elif query.data == "elimina_utente":
        keyboard = [[InlineKeyboardButton("🔙 Torna alla Gestione Utenti", callback_data="gestione_utenti")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("🗑️ Inserisci l'ID utente da eliminare:", reply_markup=reply_markup)
        context.user_data['admin_action'] = 'elimina_utente'

    elif query.data == "aggiungi_admin":
        keyboard = [[InlineKeyboardButton("🔙 Torna alla Gestione Admin", callback_data="gestione_admin")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("➕ Inserisci l'ID Telegram del nuovo admin:", reply_markup=reply_markup)
        context.user_data['admin_action'] = 'aggiungi_admin'

    elif query.data == "rimuovi_admin":
        keyboard = [[InlineKeyboardButton("🔙 Torna alla Gestione Admin", callback_data="gestione_admin")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("➖ Inserisci l'ID admin da rimuovere:", reply_markup=reply_markup)
        context.user_data['admin_action'] = 'rimuovi_admin'

    elif query.data == "reset_sistema":
        keyboard = [
            [InlineKeyboardButton("⚠️ CONFERMA RESET", callback_data="conferma_reset")],
            [InlineKeyboardButton("❌ Annulla", callback_data="annulla_reset")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("⚠️ ATTENZIONE! Questo cancellerà TUTTI i dati utenti.\nSei sicuro?", reply_markup=reply_markup)

    elif query.data == "conferma_reset":
        from main import utenti
        utenti.clear()
        await query.message.reply_text("🔄 Sistema resettato! Tutti i dati utenti sono stati cancellati.")

    elif query.data == "annulla_reset":
        await query.message.reply_text("❌ Reset annullato.")
    
    elif query.data.startswith("edit_saldo_"):
        user_id = int(query.data.split("_")[2])
        await query.message.reply_text(f"💰 Inserisci il nuovo saldo per l'utente {user_id}:")
        context.user_data['admin_action'] = 'edit_saldo'
        context.user_data['target_user_id'] = user_id
        await query.answer("Inserisci nuovo saldo")
    
    elif query.data.startswith("delete_user_"):
        user_id = int(query.data.split("_")[2])
        from main import utenti
        if user_id in utenti:
            nickname = utenti[user_id]['nickname']
            keyboard = [
                [InlineKeyboardButton("⚠️ CONFERMA ELIMINAZIONE", callback_data=f"confirm_delete_{user_id}")],
                [InlineKeyboardButton("❌ Annulla", callback_data=f"user_info_{user_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=f"⚠️ ATTENZIONE!\n\nStai per eliminare l'utente:\n👤 {nickname} (ID: {user_id})\n\nQuesta azione è irreversibile. Confermi?",
                reply_markup=reply_markup
            )
        await query.answer()
    
    elif query.data.startswith("confirm_delete_"):
        user_id = int(query.data.split("_")[2])
        from main import utenti
        if user_id in utenti:
            nickname = utenti[user_id]['nickname']
            del utenti[user_id]
            await context.bot.send_message(chat_id=user_id, text="⚠️ Il tuo account è stato rimosso dal sistema.")
            await query.edit_message_text(f"✅ Utente {nickname} (ID: {user_id}) eliminato con successo!")
        await query.answer("Utente eliminato")
    
    elif query.data.startswith("msg_user_"):
        user_id = int(query.data.split("_")[2])
        await query.message.reply_text(f"📨 Inserisci il messaggio da inviare all'utente {user_id}:")
        context.user_data['admin_action'] = 'send_msg_to_user'
        context.user_data['target_user_id'] = user_id
        await query.answer("Inserisci messaggio")

async def admin_handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    action = context.user_data.get('admin_action')
    text = update.message.text

    if action == 'send_global_announcement':
        from main import utenti
        announcement = text
        success_count = 0
        failed_count = 0
        
        # Ottieni tutti gli utenti che hanno mai avviato il bot (anche non registrati)
        # Per ora usiamo gli utenti registrati, ma potresti espandere questo
        all_users = list(utenti.keys()) if utenti else []
        
        # Invia l'annuncio a tutti gli utenti
        for user_id in all_users:
            try:
                await context.bot.send_message(
                    chat_id=user_id, 
                    text=f"📢 ANNUNCIO UFFICIALE MISTERSHOP CASINO\n\n{announcement}\n\n🤖 Messaggio da Stanley Admin"
                )
                success_count += 1
            except Exception as e:
                print(f"Errore invio a {user_id}: {e}")
                failed_count += 1
        
        result_text = f"📢 ANNUNCIO INVIATO!\n\n✅ Successi: {success_count}\n❌ Falliti: {failed_count}\n👥 Totale utenti: {len(all_users)}"
        
        if len(all_users) == 0:
            result_text = "⚠️ Nessun utente registrato trovato! L'annuncio non è stato inviato a nessuno."
        
        await update.message.reply_text(result_text)

    elif action == 'motivazione_rifiuto_ricarica':
        user_id = context.user_data.get('rifiuto_user_id')
        motivazione = text
        await context.bot.send_message(
            chat_id=user_id, 
            text=f"❌ La tua richiesta di ricarica è stata RIFIUTATA.\n\n📝 Motivazione:\n{motivazione}\n\n📞 Contatta l'admin per maggiori informazioni."
        )
        try:
            original_msg_id = context.user_data.get('original_message_id')
            await context.bot.edit_message_caption(
                chat_id=update.effective_chat.id,
                message_id=original_msg_id,
                caption=f"❌ Ricarica RIFIUTATA\n📝 Motivazione: {motivazione}"
            )
        except:
            pass
        await update.message.reply_text("✅ Rifiuto inviato con motivazione.")

    elif action == 'motivazione_rifiuto_reg':
        user_id = context.user_data.get('rifiuto_user_id')
        motivazione = text
        await context.bot.send_message(
            chat_id=user_id, 
            text=f"❌ La tua registrazione è stata RIFIUTATA.\n\n📝 Motivazione:\n{motivazione}\n\n📞 Contatta l'admin per maggiori informazioni."
        )
        await update.message.reply_text("✅ Rifiuto registrazione inviato con motivazione.")

    elif action == 'motivazione_rifiuto_prelievo':
        user_id = context.user_data.get('rifiuto_user_id')
        motivazione = text
        await context.bot.send_message(
            chat_id=user_id, 
            text=f"❌ La tua richiesta di prelievo è stata RIFIUTATA.\n\n📝 Motivazione:\n{motivazione}\n\n📞 Contatta l'admin per maggiori informazioni."
        )
        await update.message.reply_text("✅ Rifiuto prelievo inviato con motivazione.")

    elif action == 'cerca_utente':
        try:
            user_id = int(text)
            from main import utenti
            if user_id in utenti:
                info = utenti[user_id]
                risultato = f"👤 UTENTE TROVATO:\n\n🆔 ID: {user_id}\n👤 Nickname: {info['nickname']}\n💰 Saldo: {info['saldo']}€"
            else:
                risultato = f"❌ Utente con ID {user_id} non trovato."
            await update.message.reply_text(risultato)
        except ValueError:
            await update.message.reply_text("❌ Inserisci un ID valido.")

    elif action == 'elimina_utente':
        try:
            user_id = int(text)
            from main import utenti
            if user_id in utenti:
                del utenti[user_id]
                await update.message.reply_text(f"✅ Utente {user_id} eliminato dal sistema.")
                await context.bot.send_message(chat_id=user_id, text="⚠️ Il tuo account è stato rimosso dal sistema.")
            else:
                await update.message.reply_text(f"❌ Utente {user_id} non trovato.")
        except ValueError:
            await update.message.reply_text("❌ Inserisci un ID valido.")

    elif action == 'aggiungi_admin':
        try:
            new_admin_id = int(text)
            if new_admin_id not in ADMIN_IDS:
                ADMIN_IDS.append(new_admin_id)
                await update.message.reply_text(f"✅ Admin {new_admin_id} aggiunto con successo!")
                await context.bot.send_message(chat_id=new_admin_id, text="🔧 Sei stato promosso ad Admin!")
            else:
                await update.message.reply_text("❌ Questo utente è già admin.")
        except ValueError:
            await update.message.reply_text("❌ Inserisci un ID valido.")

    elif action == 'rimuovi_admin':
        try:
            admin_id = int(text)
            if admin_id in ADMIN_IDS and len(ADMIN_IDS) > 1:
                ADMIN_IDS.remove(admin_id)
                await update.message.reply_text(f"✅ Admin {admin_id} rimosso con successo!")
                await context.bot.send_message(chat_id=admin_id, text="⚠️ I tuoi privilegi admin sono stati revocati.")
            elif admin_id not in ADMIN_IDS:
                await update.message.reply_text("❌ Questo utente non è admin.")
            else:
                await update.message.reply_text("❌ Non puoi rimuovere l'ultimo admin!")
        except ValueError:
            await update.message.reply_text("❌ Inserisci un ID valido.")
    
    elif action == 'edit_saldo':
        try:
            new_saldo = int(text)
            target_user_id = context.user_data.get('target_user_id')
            from main import utenti
            if target_user_id in utenti:
                old_saldo = utenti[target_user_id]['saldo']
                utenti[target_user_id]['saldo'] = new_saldo
                nickname = utenti[target_user_id]['nickname']
                
                await context.bot.send_message(
                    chat_id=target_user_id, 
                    text=f"💰 Il tuo saldo è stato modificato da un admin!\n\n"
                         f"📊 Saldo precedente: {old_saldo}€\n"
                         f"💰 Nuovo saldo: {new_saldo}€"
                )
                await update.message.reply_text(
                    f"✅ Saldo modificato con successo!\n\n"
                    f"👤 Utente: {nickname}\n"
                    f"📊 Vecchio saldo: {old_saldo}€\n"
                    f"💰 Nuovo saldo: {new_saldo}€"
                )
            else:
                await update.message.reply_text("❌ Utente non trovato.")
        except ValueError:
            await update.message.reply_text("❌ Inserisci un numero valido per il saldo.")
    
    elif action == 'send_msg_to_user':
        target_user_id = context.user_data.get('target_user_id')
        message = text
        try:
            await context.bot.send_message(
                chat_id=target_user_id, 
                text=f"📩 Messaggio dall'admin:\n\n{message}"
            )
            await update.message.reply_text("✅ Messaggio inviato con successo!")
        except Exception as e:
            await update.message.reply_text(f"❌ Errore nell'invio del messaggio: {str(e)}")

    context.user_data.clear()

async def show_users_page(query, context, page_num):
    from main import utenti
    users_per_page = 10
    start_idx = page_num * users_per_page
    end_idx = start_idx + users_per_page
    
    user_list = list(utenti.items())
    page_users = user_list[start_idx:end_idx]
    total_users = len(user_list)
    total_pages = (total_users + users_per_page - 1) // users_per_page
    
    if not page_users:
        await query.message.reply_text("📭 Nessun utente in questa pagina.")
        return
    
    keyboard = []
    
    # Aggiungi bottoni per ogni utente nella pagina corrente
    for user_id, info in page_users:
        # Crea una label più informativa per il bottone
        if 'username' in info and info['username'] != 'senza_username':
            label = f"👤 {info['nickname']} - @{info['username']}"
        else:
            label = f"👤 {info['nickname']} (ID: {user_id})"
        
        keyboard.append([InlineKeyboardButton(
            label, 
            callback_data=f"user_info_{user_id}"
        )])
    
    # Aggiungi controlli di navigazione se necessario
    nav_buttons = []
    if page_num > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Precedente", callback_data=f"user_page_{page_num-1}"))
    if page_num < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Successiva ➡️", callback_data=f"user_page_{page_num+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Bottone per tornare al menu
    keyboard.append([InlineKeyboardButton("🔙 Torna al Menu", callback_data="gestione_utenti")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    header = f"👥 UTENTI REGISTRATI (Pagina {page_num + 1}/{total_pages})\n"
    header += f"📊 Totale utenti: {total_users}\n\n"
    header += "Seleziona un utente per vedere i dettagli:"
    
    await query.edit_message_text(text=header, reply_markup=reply_markup)

async def show_user_details(query, context, user_id):
    from main import utenti
    
    if user_id not in utenti:
        await query.answer("❌ Utente non trovato")
        return
    
    user_info = utenti[user_id]
    
    # Usa le informazioni salvate se disponibili, altrimenti prova a recuperarle
    if 'first_name' in user_info and 'username' in user_info:
        first_name = user_info['first_name']
        last_name = user_info.get('last_name', '')
        username = f"@{user_info['username']}" if user_info['username'] != 'senza_username' else "Nessun username"
        full_name = f"{first_name} {last_name}".strip()
    else:
        # Fallback: prova a recuperare le info da Telegram
        try:
            user_obj = await context.bot.get_chat(user_id)
            first_name = user_obj.first_name or "N/A"
            last_name = user_obj.last_name or ""
            username = f"@{user_obj.username}" if user_obj.username else "Nessun username"
            full_name = f"{first_name} {last_name}".strip()
        except:
            full_name = "Informazioni non disponibili"
            username = "N/A"
    
    details = f"👤 DETTAGLI UTENTE COMPLETI:\n\n"
    details += f"🆔 ID Telegram: {user_id}\n"
    details += f"👤 Nome completo: {full_name}\n"
    details += f"📱 Username: {username}\n"
    details += f"🎮 Nickname: {user_info['nickname']}\n"
    details += f"💰 Saldo attuale: {user_info['saldo']}€\n"
    details += f"🔐 Account status: ✅ Registrato\n"
    if 'registration_date' in user_info:
        details += f"📅 Data registrazione: {user_info['registration_date']}\n"
    
    keyboard = [
        [InlineKeyboardButton("💰 Modifica Saldo", callback_data=f"edit_saldo_{user_id}")],
        [InlineKeyboardButton("🗑️ Elimina Utente", callback_data=f"delete_user_{user_id}")],
        [InlineKeyboardButton("📨 Invia Messaggio", callback_data=f"msg_user_{user_id}")],
        [InlineKeyboardButton("🔙 Torna alla Lista", callback_data="lista_utenti")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=details, reply_markup=reply_markup)
