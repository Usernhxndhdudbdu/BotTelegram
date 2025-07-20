from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from config import EMOJI, ADMIN_IDS
from utils.keyboards import RecruitmentKeyboard
from handlers.states import RecruitmentStates
from database import Database
from datetime import datetime

router = Router()

async def cmd_curriculum(message: Message, db: Database, state: FSMContext):
    """Handle /curriculum command"""
    curriculum_text = f"📝 **Candidatura Lavorativa - {message.from_user.full_name}**\n\n"
    curriculum_text += "🎯 **Posizioni Disponibili:**\n"
    curriculum_text += "👨‍🍳 Cuoco - Prepara i nostri deliziosi piatti\n"
    curriculum_text += "🧑‍💼 Cameriere - Serve i clienti con un sorriso\n"
    curriculum_text += "👔 Manager - Gestisce il ristorante\n"
    curriculum_text += "🧹 Addetto alle pulizie - Mantiene tutto pulito\n"
    curriculum_text += "🚚 Delivery - Consegna a domicilio\n\n"
    curriculum_text += "📋 **Processo di candidatura:**\n"
    curriculum_text += "• Compila il form con i tuoi dati\n"
    curriculum_text += "• Lo staff esaminerà la candidatura\n"
    curriculum_text += "• Riceverai una risposta in privato\n\n"
    curriculum_text += "Vuoi iniziare la candidatura?"

    await message.answer(
        curriculum_text,
        reply_markup=RecruitmentKeyboard.start_application()
    )

async def handle_start_application(callback: CallbackQuery, state: FSMContext):
    """Start the application process"""
    await state.set_state(RecruitmentStates.waiting_for_minecraft_name)

    try:
        await callback.message.edit_text(
            "🎮 **Domanda 1/9: Nome Minecraft**\n\n"
            "Scrivi il tuo nome Minecraft:",
            reply_markup=RecruitmentKeyboard.cancel_application()
        )
    except TelegramBadRequest:
        pass

    await callback.answer()

async def handle_minecraft_name_input(message: Message, state: FSMContext):
    """Handle minecraft name input"""
    await state.update_data(minecraft_name=message.text)
    await state.set_state(RecruitmentStates.waiting_for_telegram)

    await message.answer(
        "📱 **Domanda 2/9: @Telegram**\n\n"
        "Scrivi il tuo username Telegram (con @):",
        reply_markup=RecruitmentKeyboard.cancel_application()
    )

async def handle_telegram_input(message: Message, state: FSMContext):
    """Handle telegram input"""
    await state.update_data(telegram=message.text)
    await state.set_state(RecruitmentStates.waiting_for_presentation)

    await message.answer(
        "👋 **Domanda 3/9: Presentati**\n\n"
        "Fai una breve presentazione di te stesso:",
        reply_markup=RecruitmentKeyboard.cancel_application()
    )

async def handle_presentation_input(message: Message, state: FSMContext):
    """Handle presentation input"""
    await state.update_data(presentation=message.text)
    await state.set_state(RecruitmentStates.waiting_for_reason)

    await message.answer(
        "❓ **Domanda 4/9: Motivazione**\n\n"
        "Per quale motivo hai deciso di candidarti?",
        reply_markup=RecruitmentKeyboard.cancel_application()
    )

async def handle_reason_input(message: Message, state: FSMContext):
    """Handle reason input"""
    await state.update_data(reason=message.text)
    await state.set_state(RecruitmentStates.waiting_for_experience)

    await message.answer(
        "👨‍🍳 **Domanda 5/9: Esperienza**\n\n"
        "Hai qualche esperienza in ambito culinario e da cassiere?",
        reply_markup=RecruitmentKeyboard.cancel_application()
    )

async def handle_experience_input(message: Message, state: FSMContext):
    """Handle experience input"""
    await state.update_data(experience=message.text)
    await state.set_state(RecruitmentStates.waiting_for_hours)

    await message.answer(
        "⏰ **Domanda 6/9: Ore di lavoro**\n\n"
        "Quante ore fai normalmente?",
        reply_markup=RecruitmentKeyboard.cancel_application()
    )

async def handle_hours_input(message: Message, state: FSMContext):
    """Handle hours input"""
    await state.update_data(hours=message.text)
    await state.set_state(RecruitmentStates.waiting_for_advice)

    await message.answer(
        "💡 **Domanda 7/9: Consigli**\n\n"
        "Hai qualche consiglio da dare per migliorare l'azienda?",
        reply_markup=RecruitmentKeyboard.cancel_application()
    )

async def handle_advice_input(message: Message, state: FSMContext):
    """Handle advice input"""
    await state.update_data(advice=message.text)
    await state.set_state(RecruitmentStates.waiting_for_bad_employee)

    await message.answer(
        "⚠️ **Domanda 8/9: Dipendente problematico**\n\n"
        "Se un dipendente si comporta male, insultando tutti, o magari ha rubato 3/4 di ingredienti. Tu cosa faresti se te ne accorgessi?",
        reply_markup=RecruitmentKeyboard.cancel_application()
    )

async def handle_bad_employee_input(message: Message, state: FSMContext):
    """Handle bad employee input"""
    await state.update_data(bad_employee=message.text)
    await state.set_state(RecruitmentStates.waiting_for_additional)

    await message.answer(
        "📝 **Domanda 9/9: Altro**\n\n"
        "Hai altro da scrivere? Fallo pure in questo punto:",
        reply_markup=RecruitmentKeyboard.additional_info()
    )

async def handle_additional_input(message: Message, state: FSMContext, db: Database, bot: Bot):
    """Handle additional information input"""
    data = await state.get_data()
    username = message.from_user.username or message.from_user.full_name

    # Submit application with user input
    await submit_application(
        message, 
        state, 
        db, 
        bot,
        additional_info=message.text,
        user_id=message.from_user.id,
        username=username
    )

async def submit_application(message, state: FSMContext, db: Database, bot: Bot, additional_info: str, user_id: int, username: str):
    """Submit application helper function"""
    data = await state.get_data()

    # Create application
    app_id = db.create_application(
        user_id=user_id,
        username=username,
        full_name=message.from_user.full_name,
        minecraft_name=data.get('minecraft_name', 'N/A'),
        telegram=data.get('telegram', 'N/A'),
        presentation=data.get('presentation', 'N/A'),
        reason=data.get('reason', 'N/A'),
        experience=data.get('experience', 'N/A'),
        hours=data.get('hours', 'N/A'),
        advice=data.get('advice', 'N/A'),
        bad_employee=data.get('bad_employee', 'N/A'),
        additional=additional_info
    )

    # Send confirmation to user
    current_date = db.get_current_time().strftime("%Y-%m-%d")
    await message.answer(
        f"✅ **Candidatura Inviata!**\n\n"
        f"🆔 ID Candidatura: `{app_id}`\n"
        f"📅 Data: {current_date}\n\n"
        f"La tua candidatura è stata inviata allo staff per la valutazione.\n"
        f"Riceverai una risposta nelle prossime ore.",
        reply_markup=RecruitmentKeyboard.back_to_menu()
    )

    # Send to staff group
    staff_group_id = db.get_staff_group_id()
    applications_topic_id = db.get_topic_id("applications")

    if staff_group_id:
        try:
            current_date = db.get_current_time().strftime("%Y-%m-%d")
            staff_text = f"📝 **Nuova Candidatura #{app_id}**\n\n"
            staff_text += f"👤 **Candidato:** {message.from_user.full_name} (@{message.from_user.username or 'N/A'})\n"
            staff_text += f"🆔 **User ID:** `{message.from_user.id}`\n"
            staff_text += f"📅 **Data:** {current_date}\n\n"

            staff_text += f"🎮 **Nome Minecraft:** `{data.get('minecraft_name', 'N/A')}`\n"
            staff_text += f"📱 **Telegram:** `{data.get('telegram', 'N/A')}`\n\n"

            staff_text += f"👋 **Presentazione:**\n`{data.get('presentation', 'N/A')}`\n\n"
            staff_text += f"❓ **Motivazione:**\n`{data.get('reason', 'N/A')}`\n\n"
            staff_text += f"👨‍🍳 **Esperienza:**\n`{data.get('experience', 'N/A')}`\n\n"
            staff_text += f"⏰ **Ore di lavoro:**\n`{data.get('hours', 'N/A')}`\n\n"
            staff_text += f"💡 **Consigli:**\n`{data.get('advice', 'N/A')}`\n\n"
            staff_text += f"⚠️ **Dipendente problematico:**\n`{data.get('bad_employee', 'N/A')}`\n\n"
            staff_text += f"📝 **Altro:**\n{additional_info}\n\n"

            staff_text += f"⏳ **Stato:** In attesa di valutazione"

            if applications_topic_id:
                await bot.send_message(
                    chat_id=staff_group_id,
                    message_thread_id=applications_topic_id,
                    text=staff_text,
                    reply_markup=RecruitmentKeyboard.staff_application_actions(app_id)
                )
            else:
                await bot.send_message(
                    chat_id=staff_group_id,
                    text=staff_text,
                    reply_markup=RecruitmentKeyboard.staff_application_actions(app_id)
                )
        except Exception as e:
            print(f"Error sending application to staff group: {e}")

    await state.clear()

async def handle_cancel_application(callback: CallbackQuery, state: FSMContext):
    """Handle application cancellation"""
    await state.clear()

    try:
        await callback.message.edit_text(
            "❌ **Candidatura Annullata**\n\n"
            "Puoi riavviare il processo in qualsiasi momento con /curriculum",
            reply_markup=RecruitmentKeyboard.back_to_menu()
        )
    except TelegramBadRequest:
        pass

    await callback.answer("Candidatura annullata!")

async def handle_write_additional_info(callback: CallbackQuery, state: FSMContext):
    """Handle write additional info"""
    await state.set_state(RecruitmentStates.waiting_for_additional_text)
    
    try:
        await callback.message.edit_text(
            "📝 **Domanda 9/9: Altro**\n\n"
            "✍️ Scrivi quello che vuoi aggiungere alla tua candidatura:",
            reply_markup=RecruitmentKeyboard.cancel_application()
        )
    except TelegramBadRequest:
        pass
    
    await callback.answer()

async def handle_additional_text_input(message: Message, state: FSMContext, db: Database, bot: Bot):
    """Handle additional text input"""
    # Submit application with user input
    await submit_application(
        message, 
        state, 
        db, 
        bot,
        additional_info=f"`{message.text}`",
        user_id=message.from_user.id,
        username=message.from_user.username or message.from_user.full_name
    )

async def handle_no_additional_info(callback: CallbackQuery, state: FSMContext, db: Database, bot: Bot):
    """Handle no additional info submission"""
    # Submit application automatically
    await submit_application(
        callback.message, 
        state, 
        db, 
        bot,
        additional_info="`Non ho nulla da dire`",
        user_id=callback.from_user.id,
        username=callback.from_user.username or callback.from_user.full_name
    )

    await callback.answer("✅ Candidatura inviata!")

async def handle_staff_application_action(callback: CallbackQuery, db: Database, bot: Bot):
    """Handle staff application approval/rejection"""
    action = callback.data.split(":")[1]
    app_id = callback.data.split(":")[2]

    application = db.get_application(app_id)
    if not application:
        await callback.answer("❌ Candidatura non trovata!", show_alert=True)
        return

    if action == "approve":
        db.update_application_status(app_id, "approved")
        status_text = "✅ Approvata"
        user_message = f"🎉 Congratulazioni! La tua candidatura `{app_id}` è stata approvata!\n\nVerrai contattato dallo staff per i prossimi passi."
    else:
        db.update_application_status(app_id, "rejected")
        status_text = "❌ Rifiutata"
        user_message = f"😔 La tua candidatura `{app_id}` non è stata accettata questa volta.\n\nPuoi riprovare in futuro!"

    # Update message
    try:
        current_text = callback.message.text
        updated_text = current_text.replace("⏳ **Stato:** In attesa di valutazione", f"**Stato:** {status_text}")

        await callback.message.edit_text(
            updated_text,
            reply_markup=None
        )

    except TelegramBadRequest:
        pass

    # Send notification to user
    try:
        await bot.send_message(
            chat_id=application["user_id"],
            text=user_message
        )
    except Exception as e:
        print(f"Error sending notification to user: {e}")

    await callback.answer(f"✅ Candidatura {action}!")

def register_handlers(dp, db: Database, bot: Bot):
    """Register recruitment handlers"""

    @dp.message(Command("curriculum"))
    async def curriculum_handler(message: Message, state: FSMContext):
        await cmd_curriculum(message, db, state)

    @dp.callback_query(lambda c: c.data == "start_application")
    async def start_application_handler(callback: CallbackQuery, state: FSMContext):
        await handle_start_application(callback, state)

    @dp.message(RecruitmentStates.waiting_for_minecraft_name)
    async def minecraft_name_handler(message: Message, state: FSMContext):
        await handle_minecraft_name_input(message, state)

    @dp.message(RecruitmentStates.waiting_for_telegram)
    async def telegram_handler(message: Message, state: FSMContext):
        await handle_telegram_input(message, state)

    @dp.message(RecruitmentStates.waiting_for_presentation)
    async def presentation_handler(message: Message, state: FSMContext):
        await handle_presentation_input(message, state)

    @dp.message(RecruitmentStates.waiting_for_reason)
    async def reason_handler(message: Message, state: FSMContext):
        await handle_reason_input(message, state)

    @dp.message(RecruitmentStates.waiting_for_experience)
    async def experience_handler(message: Message, state: FSMContext):
        await handle_experience_input(message, state)

    @dp.message(RecruitmentStates.waiting_for_hours)
    async def hours_handler(message: Message, state: FSMContext):
        await handle_hours_input(message, state)

    @dp.message(RecruitmentStates.waiting_for_advice)
    async def advice_handler(message: Message, state: FSMContext):
        await handle_advice_input(message, state)

    @dp.message(RecruitmentStates.waiting_for_bad_employee)
    async def bad_employee_handler(message: Message, state: FSMContext):
        await handle_bad_employee_input(message, state)

    @dp.message(RecruitmentStates.waiting_for_additional)
    async def additional_handler(message: Message, state: FSMContext):
        await handle_additional_input(message, state, db, bot)

    @dp.callback_query(lambda c: c.data == "cancel_application")
    async def cancel_application_handler(callback: CallbackQuery, state: FSMContext):
        await handle_cancel_application(callback, state)
        
    @dp.callback_query(lambda c: c.data == "write_additional")
    async def write_additional_handler(callback: CallbackQuery, state: FSMContext):
        await handle_write_additional_info(callback, state)
    
    @dp.message(RecruitmentStates.waiting_for_additional_text)
    async def additional_text_handler(message: Message, state: FSMContext):
        await handle_additional_text_input(message, state, db, bot)
    
    @dp.callback_query(lambda c: c.data == "no_additional_info")
    async def no_additional_info_handler(callback: CallbackQuery, state: FSMContext):
        await handle_no_additional_info(callback, state, db, bot)

    @dp.callback_query(lambda c: c.data.startswith("app_action:"))
    async def staff_application_handler(callback: CallbackQuery):
        await handle_staff_application_action(callback, db, bot)