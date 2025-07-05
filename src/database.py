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
        try:
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
                        billing_date INTEGER,
                        bill_amount DECIMAL(10,2),
                        last_bill_date DATE,
                        next_bill_date DATE,
                        bill_status TEXT DEFAULT 'pending',
                        payment_grace_days INTEGER DEFAULT 21,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, card_number)
                    )
                ''')
                
                # Create user sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER UNIQUE NOT NULL,
                        current_state TEXT NOT NULL,
                        form_data TEXT,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Migrate existing database to add billing columns if they don't exist
                self._migrate_database(cursor)
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def _migrate_database(self, cursor):
        """Migrate database schema to add billing columns if they don't exist."""
        try:
            # Check if billing_date column exists
            cursor.execute("PRAGMA table_info(credit_cards)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Add billing columns if they don't exist
            if 'billing_date' not in columns:
                logger.info("Adding billing_date column to credit_cards table")
                cursor.execute('ALTER TABLE credit_cards ADD COLUMN billing_date INTEGER')
            
            if 'bill_amount' not in columns:
                logger.info("Adding bill_amount column to credit_cards table")
                cursor.execute('ALTER TABLE credit_cards ADD COLUMN bill_amount DECIMAL(10,2)')
            
            if 'last_bill_date' not in columns:
                logger.info("Adding last_bill_date column to credit_cards table")
                cursor.execute('ALTER TABLE credit_cards ADD COLUMN last_bill_date DATE')
            
            if 'next_bill_date' not in columns:
                logger.info("Adding next_bill_date column to credit_cards table")
                cursor.execute('ALTER TABLE credit_cards ADD COLUMN next_bill_date DATE')
            
            if 'bill_status' not in columns:
                logger.info("Adding bill_status column to credit_cards table")
                cursor.execute('ALTER TABLE credit_cards ADD COLUMN bill_status TEXT DEFAULT "pending"')
            
            if 'payment_grace_days' not in columns:
                logger.info("Adding payment_grace_days column to credit_cards table")
                cursor.execute('ALTER TABLE credit_cards ADD COLUMN payment_grace_days INTEGER DEFAULT 21')
            
            logger.info("Database migration completed successfully")
        except Exception as e:
            logger.error(f"Error during database migration: {e}")
            raise
    
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
    
    def update_billing_info(self, user_id: int, card_id: int, billing_date: int, bill_amount: float, grace_days: int = 21):
        """Update billing information for a card."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Calculate next bill date
                from datetime import datetime, timedelta
                today = datetime.now()
                
                # Set next bill date to billing_date of current/next month
                next_bill = today.replace(day=billing_date)
                if next_bill <= today:
                    # If billing date has passed this month, set to next month
                    if next_bill.month == 12:
                        next_bill = next_bill.replace(year=next_bill.year + 1, month=1)
                    else:
                        next_bill = next_bill.replace(month=next_bill.month + 1)
                
                cursor.execute('''
                    UPDATE credit_cards 
                    SET billing_date = ?, bill_amount = ?, next_bill_date = ?, 
                        payment_grace_days = ?, bill_status = 'pending', updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND id = ?
                ''', (billing_date, bill_amount, next_bill.date(), grace_days, user_id, card_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating billing info: {e}")
            return False
    
    def mark_bill_paid(self, user_id: int, card_id: int):
        """Mark a bill as paid and calculate next bill date."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get current billing info
                cursor.execute('''
                    SELECT billing_date, next_bill_date, payment_grace_days FROM credit_cards 
                    WHERE user_id = ? AND id = ?
                ''', (user_id, card_id))
                result = cursor.fetchone()
                
                if not result:
                    return False
                
                billing_date, current_next_bill, grace_days = result
                grace_days = grace_days or 21  # Default to 21 if not set
                
                # Calculate next bill date
                from datetime import datetime, timedelta
                if current_next_bill:
                    next_bill = datetime.strptime(current_next_bill, '%Y-%m-%d')
                else:
                    next_bill = datetime.now()
                
                # Add one month to next bill date
                if next_bill.month == 12:
                    next_bill = next_bill.replace(year=next_bill.year + 1, month=1)
                else:
                    next_bill = next_bill.replace(month=next_bill.month + 1)
                
                cursor.execute('''
                    UPDATE credit_cards 
                    SET last_bill_date = ?, next_bill_date = ?, 
                        bill_status = 'paid', updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND id = ?
                ''', (current_next_bill, next_bill.date(), user_id, card_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error marking bill as paid: {e}")
            return False
    
    def get_pending_bills(self, user_id: int):
        """Get all pending bills for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM credit_cards 
                    WHERE user_id = ? AND bill_status = 'pending' 
                    AND next_bill_date IS NOT NULL
                    ORDER BY next_bill_date ASC
                ''', (user_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting pending bills: {e}")
            return []
    
    def get_due_bills(self, user_id: int):
        """Get bills that are due or overdue."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM credit_cards 
                    WHERE user_id = ? AND bill_status = 'pending' 
                    AND next_bill_date <= DATE('now')
                    ORDER BY next_bill_date ASC
                ''', (user_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting due bills: {e}")
            return []
    
    def update_bill_amount(self, user_id: int, card_id: int, new_amount: float):
        """Update bill amount for an existing card."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE credit_cards 
                    SET bill_amount = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND id = ?
                ''', (new_amount, user_id, card_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating bill amount: {e}")
            return False
    
    def update_payment_grace_days(self, user_id: int, card_id: int, grace_days: int):
        """Update payment grace days for a card."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE credit_cards 
                    SET payment_grace_days = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND id = ?
                ''', (grace_days, user_id, card_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating payment grace days: {e}")
            return False 