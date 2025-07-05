#!/usr/bin/env python3
"""
Credit Card Management Bot
A secure Telegram bot for managing credit card information with user isolation.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.bot import main

if __name__ == "__main__":
    main() 