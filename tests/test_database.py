"""
Credit Card Management Bot - Database Tests
Unit tests for database operations.

Copyright (C) 2025  Abhiram Shibu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import pytest
import tempfile
import os
from src.database import DatabaseManager

class TestDatabaseManager:
    """Test cases for DatabaseManager."""
    
    @pytest.fixture
    def db_manager(self):
        """Create a temporary database for testing."""
        # Create a temporary file for the database
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        db_manager = DatabaseManager(temp_db.name)
        yield db_manager
        
        # Cleanup: remove the temporary database file
        os.unlink(temp_db.name)
    
    def test_init_database(self, db_manager):
        """Test database initialization."""
        # Check if tables were created
        import sqlite3
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.cursor()
            
            # Check credit_cards table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='credit_cards'")
            assert cursor.fetchone() is not None
            
            # Check user_sessions table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_sessions'")
            assert cursor.fetchone() is not None
    
    def test_add_credit_card_success(self, db_manager):
        """Test successful credit card addition."""
        user_id = 12345
        bank_name = "HDFC"
        card_number = "1234"
        expiry_date = "12/2025"
        
        result = db_manager.add_credit_card(user_id, bank_name, card_number, expiry_date)
        assert result is True
        
        # Verify the card was added
        cards = db_manager.get_user_cards(user_id)
        assert len(cards) == 1
        assert cards[0]['bank_name'] == bank_name
        assert cards[0]['card_number'] == card_number
        assert cards[0]['expiry_date'] == expiry_date
        assert cards[0]['user_id'] == user_id
    
    def test_add_credit_card_with_cvv(self, db_manager):
        """Test credit card addition with CVV."""
        user_id = 12345
        bank_name = "SBI"
        card_number = "5678"
        expiry_date = "06/2026"
        cvv = "123"
        full_card_number = "1234567890123456"
        
        result = db_manager.add_credit_card(
            user_id, bank_name, card_number, expiry_date, cvv, full_card_number
        )
        assert result is True
        
        # Verify the card was added with CVV
        cards = db_manager.get_user_cards(user_id)
        assert len(cards) == 1
        assert cards[0]['cvv'] == cvv
        assert cards[0]['full_card_number'] == full_card_number
    
    def test_add_duplicate_card(self, db_manager):
        """Test adding duplicate card (should fail)."""
        user_id = 12345
        bank_name = "HDFC"
        card_number = "1234"
        expiry_date = "12/2025"
        
        # Add first card
        result1 = db_manager.add_credit_card(user_id, bank_name, card_number, expiry_date)
        assert result1 is True
        
        # Try to add duplicate card
        result2 = db_manager.add_credit_card(user_id, bank_name, card_number, expiry_date)
        assert result2 is False
        
        # Should still have only one card
        cards = db_manager.get_user_cards(user_id)
        assert len(cards) == 1
    
    def test_get_user_cards_empty(self, db_manager):
        """Test getting cards for user with no cards."""
        user_id = 99999
        cards = db_manager.get_user_cards(user_id)
        assert cards == []
    
    def test_get_user_cards_multiple(self, db_manager):
        """Test getting multiple cards for a user."""
        user_id = 12345
        
        # Add multiple cards
        db_manager.add_credit_card(user_id, "HDFC", "1234", "12/2025")
        db_manager.add_credit_card(user_id, "SBI", "5678", "06/2026")
        db_manager.add_credit_card(user_id, "ICICI", "9012", "03/2027")
        
        cards = db_manager.get_user_cards(user_id)
        assert len(cards) == 3
        
        # Check that all cards are present (order may vary due to timing)
        bank_names = [card['bank_name'] for card in cards]
        assert "HDFC" in bank_names
        assert "SBI" in bank_names
        assert "ICICI" in bank_names
    
    def test_user_isolation(self, db_manager):
        """Test that users can only see their own cards."""
        user1_id = 11111
        user2_id = 22222
        
        # Add cards for both users
        db_manager.add_credit_card(user1_id, "HDFC", "1234", "12/2025")
        db_manager.add_credit_card(user2_id, "SBI", "5678", "06/2026")
        
        # User 1 should only see their card
        user1_cards = db_manager.get_user_cards(user1_id)
        assert len(user1_cards) == 1
        assert user1_cards[0]['bank_name'] == "HDFC"
        
        # User 2 should only see their card
        user2_cards = db_manager.get_user_cards(user2_id)
        assert len(user2_cards) == 1
        assert user2_cards[0]['bank_name'] == "SBI"
    
    def test_get_card_by_id(self, db_manager):
        """Test getting a specific card by ID."""
        user_id = 12345
        db_manager.add_credit_card(user_id, "HDFC", "1234", "12/2025")
        
        # Get the card ID
        cards = db_manager.get_user_cards(user_id)
        card_id = cards[0]['id']
        
        # Get card by ID
        card = db_manager.get_card_by_id(user_id, card_id)
        assert card is not None
        assert card['bank_name'] == "HDFC"
        assert card['card_number'] == "1234"
    
    def test_get_card_by_id_wrong_user(self, db_manager):
        """Test getting card by ID with wrong user (should fail)."""
        user1_id = 11111
        user2_id = 22222
        
        db_manager.add_credit_card(user1_id, "HDFC", "1234", "12/2025")
        
        # Get the card ID
        cards = db_manager.get_user_cards(user1_id)
        card_id = cards[0]['id']
        
        # Try to get card with wrong user ID
        card = db_manager.get_card_by_id(user2_id, card_id)
        assert card is None
    
    def test_search_cards_by_bank(self, db_manager):
        """Test searching cards by bank name."""
        user_id = 12345
        db_manager.add_credit_card(user_id, "HDFC", "1234", "12/2025")
        db_manager.add_credit_card(user_id, "HDFC Premium", "5678", "06/2026")
        db_manager.add_credit_card(user_id, "SBI", "9012", "03/2027")
        
        # Search for HDFC cards
        hdfc_cards = db_manager.get_cards_by_bank_or_number(user_id, "HDFC")
        assert len(hdfc_cards) == 2
        
        # Search for SBI cards
        sbi_cards = db_manager.get_cards_by_bank_or_number(user_id, "SBI")
        assert len(sbi_cards) == 1
    
    def test_search_cards_by_number(self, db_manager):
        """Test searching cards by card number."""
        user_id = 12345
        db_manager.add_credit_card(user_id, "HDFC", "1234", "12/2025")
        db_manager.add_credit_card(user_id, "SBI", "5678", "06/2026")
        
        # Search by last 4 digits
        cards = db_manager.get_cards_by_bank_or_number(user_id, "1234")
        assert len(cards) == 1
        assert cards[0]['bank_name'] == "HDFC"
    
    def test_delete_card_success(self, db_manager):
        """Test successful card deletion."""
        user_id = 12345
        db_manager.add_credit_card(user_id, "HDFC", "1234", "12/2025")
        
        # Get the card ID
        cards = db_manager.get_user_cards(user_id)
        card_id = cards[0]['id']
        
        # Delete the card
        result = db_manager.delete_card(user_id, card_id)
        assert result is True
        
        # Verify card was deleted
        remaining_cards = db_manager.get_user_cards(user_id)
        assert len(remaining_cards) == 0
    
    def test_delete_card_wrong_user(self, db_manager):
        """Test deleting card with wrong user (should fail)."""
        user1_id = 11111
        user2_id = 22222
        
        db_manager.add_credit_card(user1_id, "HDFC", "1234", "12/2025")
        
        # Get the card ID
        cards = db_manager.get_user_cards(user1_id)
        card_id = cards[0]['id']
        
        # Try to delete with wrong user ID
        result = db_manager.delete_card(user2_id, card_id)
        assert result is False
        
        # Card should still exist
        remaining_cards = db_manager.get_user_cards(user1_id)
        assert len(remaining_cards) == 1
    
    def test_user_session_management(self, db_manager):
        """Test user session management."""
        user_id = 12345
        state = "waiting_bank_name"
        form_data = '{"bank_name": "HDFC", "card_number": ""}'
        
        # Save session
        db_manager.save_user_session(user_id, state, form_data)
        
        # Get session
        session = db_manager.get_user_session(user_id)
        assert session is not None
        assert session['current_state'] == state
        assert session['form_data'] == form_data
        assert session['user_id'] == user_id
        
        # Clear session
        db_manager.clear_user_session(user_id)
        
        # Session should be gone
        session = db_manager.get_user_session(user_id)
        assert session is None 