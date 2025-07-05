import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from .config import Config
from .database import DatabaseManager
from .form_manager import FormManager
from .handlers import CreditCardHandlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class CreditCardBot:
    """Main bot application class."""
    
    def __init__(self):
        """Initialize the bot with all components."""
        # Validate configuration
        Config.validate()
        
        # Initialize components
        self.db_manager = DatabaseManager(Config.DATABASE_PATH)
        self.form_manager = FormManager(self.db_manager)
        self.handlers = CreditCardHandlers(self.db_manager, self.form_manager)
        
        # Initialize application
        if not Config.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        self._setup_handlers()
        
        logger.info("Credit Card Bot initialized successfully")
    
    def _setup_handlers(self):
        """Setup all command and message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.handlers.start_command))
        self.application.add_handler(CommandHandler("help", self.handlers.help_command))
        self.application.add_handler(CommandHandler("add_card", self.handlers.add_card_command))
        self.application.add_handler(CommandHandler("view_cards", self.handlers.view_cards_command))
        self.application.add_handler(CommandHandler("view_card", self.handlers.view_card_command))
        self.application.add_handler(CommandHandler("delete_card", self.handlers.delete_card_command))
        
        # Callback query handler for inline keyboards
        self.application.add_handler(CallbackQueryHandler(self.handlers.handle_callback_query))
        
        # Message handler for form input
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.handle_text_message))
        
        # Error handler
        self.application.add_error_handler(self._error_handler)
        
        logger.info("All handlers registered successfully")
    
    async def _error_handler(self, update, context):
        """Handle errors in the bot."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Send a user-friendly error message
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Sorry, something went wrong. Please try again later."
            )
    
    def start(self):
        """Start the bot."""
        logger.info("Starting Credit Card Bot...")
        self.application.run_polling()
    
    def stop(self):
        """Stop the bot."""
        logger.info("Stopping Credit Card Bot...")
        self.application.stop()

def main():
    """Main entry point for the bot."""
    try:
        bot = CreditCardBot()
        bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    main() 