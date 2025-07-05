#!/usr/bin/env python3
"""
Test script to send a test message to verify bot functionality.
"""

import asyncio
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import Config
from telegram import Bot

async def send_test_message():
    """Send a test message to verify bot functionality."""
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
        print(f"✅ Bot: @{bot_info.username}")
        
        # Ask for chat ID
        print("\n📝 To test the bot, you need to:")
        print("1. Start the bot in Telegram by sending /start")
        print("2. Get your chat ID by sending a message to @userinfobot")
        print("3. Enter your chat ID below:")
        
        chat_id = input("Enter your chat ID: ").strip()
        
        if not chat_id.isdigit():
            print("❌ Invalid chat ID. Please enter a number.")
            return False
        
        # Send test message
        message = await bot.send_message(
            chat_id=int(chat_id),
            text="🤖 **Test Message**\n\nThis is a test message from your Credit Card Manager Bot!\n\nTry sending /start to begin using the bot."
        )
        
        print(f"✅ Test message sent successfully!")
        print(f"   Message ID: {message.message_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(send_test_message())
    sys.exit(0 if success else 1) 