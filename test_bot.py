#!/usr/bin/env python3
"""
Test script to check bot status and basic functionality.
"""

import asyncio
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from telegram import Bot

async def test_bot():
    """Test bot connection and basic functionality."""
    try:
        # Validate config
        Config.validate()
        print("✅ Configuration is valid")
        
        # Create bot instance
        if not Config.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        
        # Get bot info
        bot_info = await bot.get_me()
        print(f"✅ Bot connected successfully!")
        print(f"   Name: {bot_info.first_name}")
        print(f"   Username: @{bot_info.username}")
        print(f"   ID: {bot_info.id}")
        
        # Test webhook info
        webhook_info = await bot.get_webhook_info()
        print(f"   Webhook URL: {webhook_info.url or 'None'}")
        print(f"   Has custom certificate: {webhook_info.has_custom_certificate}")
        
        # If webhook is set, delete it to use polling
        if webhook_info.url:
            print("⚠️  Webhook is configured. Deleting webhook to use polling...")
            await bot.delete_webhook()
            print("✅ Webhook deleted successfully")
        
        print("\n🎉 Bot is ready to use!")
        print("   Commands available:")
        print("   - /start")
        print("   - /help") 
        print("   - /add_card")
        print("   - /view_cards")
        print("   - /view_card <search>")
        print("   - /delete_card <search>")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_bot())
    sys.exit(0 if success else 1) 