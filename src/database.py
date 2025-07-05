import sqlite3
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for credit card operations with user isolation."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create credit cards table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credit_cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    bank_name TEXT NOT NULL,
                    card_number TEXT NOT NULL,
                    expiry_date TEXT NOT NULL,
                    cvv TEXT,
                    full_card_number TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, card_number)
                )
            ''')
            
            # Create user sessions table for form state management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    user_id INTEGER PRIMARY KEY,
                    current_state TEXT,
                    form_data TEXT,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def add_credit_card(self, user_id: int, bank_name: str, card_number: str, 
                       expiry_date: str, cvv: Optional[str] = None, 
                       full_card_number: Optional[str] = None) -> bool:
        """Add a new credit card for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO credit_cards 
                    (user_id, bank_name, card_number, expiry_date, cvv, full_card_number)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, bank_name, card_number, expiry_date, cvv, full_card_number))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Card {card_number} already exists for user {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error adding credit card: {e}")
            return False
    
    def get_user_cards(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all credit cards for a specific user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM credit_cards 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC
                ''', (user_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting user cards: {e}")
            return []
    
    def get_card_by_id(self, user_id: int, card_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific credit card by ID for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM credit_cards 
                    WHERE user_id = ? AND id = ?
                ''', (user_id, card_id))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting card by ID: {e}")
            return None
    
    def get_cards_by_bank_or_number(self, user_id: int, search_term: str) -> List[Dict[str, Any]]:
        """Get cards by bank name or card number for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM credit_cards 
                    WHERE user_id = ? AND (bank_name LIKE ? OR card_number LIKE ?)
                    ORDER BY created_at DESC
                ''', (user_id, f'%{search_term}%', f'%{search_term}%'))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error searching cards: {e}")
            return []
    
    def delete_card(self, user_id: int, card_id: int) -> bool:
        """Delete a credit card for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM credit_cards 
                    WHERE user_id = ? AND id = ?
                ''', (user_id, card_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting card: {e}")
            return False
    
    def save_user_session(self, user_id: int, state: str, form_data: str):
        """Save user session state for form management."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_sessions 
                    (user_id, current_state, form_data, last_activity)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, state, form_data, datetime.now()))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving user session: {e}")
    
    def get_user_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user session state."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM user_sessions 
                    WHERE user_id = ?
                ''', (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user session: {e}")
            return None
    
    def clear_user_session(self, user_id: int):
        """Clear user session state."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM user_sessions 
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Error clearing user session: {e}") 