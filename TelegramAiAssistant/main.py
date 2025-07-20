import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_IDS
from database import Database
from handlers import menu, orders, sponsor, recruitment, admin, fallback, user_management

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KrustyKrabBot:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.db = Database()

    async def setup_bot_commands(self):
        """Setup bot commands menu"""
        commands = [
            BotCommand(command="start", description="🏠 Inizia"),
            BotCommand(command="menu", description="🍔 Visualizza il menù"),
            BotCommand(command="sponsor", description="📣 Richiedi sponsor"),
            BotCommand(command="curriculum", description="📝 Invia curriculum"),
            BotCommand(command="setup_staff", description="👥 Configura gruppo staff (Admin)"),
            BotCommand(command="create_topics", description="📋 Crea topics (Admin)"),
            BotCommand(command="gestisci_menu", description="⚙️ Gestisci menù (Admin)"),
            BotCommand(command="aggiungi_piatto", description="➕ Aggiungi piatto (Admin)")
        ]
        await self.bot.set_my_commands(commands)

    async def setup_staff_group(self):
        """Setup staff group - requires manual group creation"""
        try:
            staff_group_id = self.db.get_staff_group_id()

            if not staff_group_id:
                logger.info("Staff group not configured.")
                logger.info("To set up the staff group:")
                logger.info("1. Create a supergroup on Telegram")
                logger.info("2. Add the bot as admin with all permissions")
                logger.info("3. Enable Topics in group settings")
                logger.info("4. Get the group ID and use /setup_staff command to configure it")

                # For now, we'll skip staff group features if not configured
                # The bot will still work for basic menu and user interactions
                logger.info("Bot will work without staff group for now")
            else:
                logger.info(f"Staff group configured: {staff_group_id}")

                # Verify topics exist, if not skip topic creation
                orders_topic = self.db.get_topic_id("orders") 
                sponsors_topic = self.db.get_topic_id("sponsors")
                recruitment_topic = self.db.get_topic_id("recruitment")

                if not all([orders_topic, sponsors_topic, recruitment_topic]):
                    logger.info("Some topics not configured - staff features may not work fully")

        except Exception as e:
            logger.error(f"Error setting up staff group: {e}")

    async def register_handlers(self):
        """Register all handlers"""
        # Register handlers
        from handlers import menu, orders, sponsor, recruitment, admin, fallback, user_management

        menu.register_handlers(self.dp, self.db, self.bot)
        orders.register_handlers(self.dp, self.db, self.bot)
        sponsor.register_handlers(self.dp, self.db, self.bot)
        recruitment.register_handlers(self.dp, self.db, self.bot)
        admin.register_handlers(self.dp, self.db, self.bot)
        user_management.register_handlers(self.dp, self.db, self.bot)
        fallback.register_handlers(self.dp, self.db, self.bot)

    async def start(self):
        """Start the bot"""
        logger.info("Starting The Krusty Krab Bot...")

        await self.setup_bot_commands()
        await self.setup_staff_group()
        await self.register_handlers()

        logger.info("Bot started successfully!")
        await self.dp.start_polling(self.bot)

    async def stop(self):
        """Stop the bot"""
        logger.info("Stopping bot...")
        await self.bot.session.close()

async def main():
    """Main function"""
    bot = KrustyKrabBot()
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())