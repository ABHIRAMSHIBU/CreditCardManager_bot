"""
Credit Card Management Bot - Form Manager Tests
Unit tests for form state management.

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
from src.form_manager import FormManager, FormState

class TestFormManager:
    """Test cases for FormManager."""
    
    @pytest.fixture
    def db_manager(self):
        """Create a temporary database for testing."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        db_manager = DatabaseManager(temp_db.name)
        yield db_manager
        
        os.unlink(temp_db.name)
    
    @pytest.fixture
    def form_manager(self, db_manager):
        """Create a form manager for testing."""
        return FormManager(db_manager)
    
    def test_start_add_card_form(self, form_manager):
        """Test starting a new add card form."""
        user_id = 12345
        form_data = form_manager.start_add_card_form(user_id)
        
        # Check initial form data
        assert form_data['bank_name'] == ""
        assert form_data['card_number'] == ""
        assert form_data['expiry_date'] == ""
        assert form_data['cvv'] == ""
        assert form_data['full_card_number'] == ""
        
        # Check that session was saved
        session = form_manager.db_manager.get_user_session(user_id)
        assert session is not None
        assert session['current_state'] == FormState.IDLE.value
    
    def test_get_form_data(self, form_manager):
        """Test getting form data."""
        user_id = 12345
        form_manager.start_add_card_form(user_id)
        
        form_data = form_manager.get_form_data(user_id)
        assert form_data is not None
        assert form_data['bank_name'] == ""
        assert form_data['card_number'] == ""
    
    def test_get_form_data_nonexistent(self, form_manager):
        """Test getting form data for user with no session."""
        user_id = 99999
        form_data = form_manager.get_form_data(user_id)
        assert form_data is None
    
    def test_get_current_state(self, form_manager):
        """Test getting current form state."""
        user_id = 12345
        form_manager.start_add_card_form(user_id)
        
        state = form_manager.get_current_state(user_id)
        assert state == FormState.IDLE
    
    def test_set_state(self, form_manager):
        """Test setting form state."""
        user_id = 12345
        form_manager.start_add_card_form(user_id)
        
        # Set new state
        form_manager.set_state(user_id, FormState.WAITING_BANK_NAME)
        
        # Check state was updated
        state = form_manager.get_current_state(user_id)
        assert state == FormState.WAITING_BANK_NAME
    
    def test_update_form_field(self, form_manager):
        """Test updating form fields."""
        user_id = 12345
        form_manager.start_add_card_form(user_id)
        
        # Update bank name
        result = form_manager.update_form_field(user_id, "bank_name", "HDFC")
        assert result is True
        
        # Check field was updated
        form_data = form_manager.get_form_data(user_id)
        assert form_data['bank_name'] == "HDFC"
    
    def test_update_form_field_nonexistent_user(self, form_manager):
        """Test updating form field for user with no session."""
        user_id = 99999
        result = form_manager.update_form_field(user_id, "bank_name", "HDFC")
        assert result is False
    
    def test_is_form_complete_minimal(self, form_manager):
        """Test form completion check with minimal required fields."""
        user_id = 12345
        form_manager.start_add_card_form(user_id)
        
        # Initially incomplete
        assert form_manager.is_form_complete(user_id) is False
        
        # Add required fields
        form_manager.update_form_field(user_id, "bank_name", "HDFC")
        form_manager.update_form_field(user_id, "card_number", "1234")
        form_manager.update_form_field(user_id, "expiry_date", "12/2025")
        
        # Should be complete
        assert form_manager.is_form_complete(user_id) is True
    
    def test_is_form_complete_with_full_card(self, form_manager):
        """Test form completion check with full card number (requires CVV)."""
        user_id = 12345
        form_manager.start_add_card_form(user_id)
        
        # Add required fields but with full card number
        form_manager.update_form_field(user_id, "bank_name", "HDFC")
        form_manager.update_form_field(user_id, "card_number", "1234")
        form_manager.update_form_field(user_id, "full_card_number", "1234567890123456")
        form_manager.update_form_field(user_id, "expiry_date", "12/2025")
        
        # Should be incomplete (missing CVV)
        assert form_manager.is_form_complete(user_id) is False
        
        # Add CVV
        form_manager.update_form_field(user_id, "cvv", "123")
        
        # Should be complete
        assert form_manager.is_form_complete(user_id) is True
    
    def test_clear_form(self, form_manager):
        """Test clearing form data."""
        user_id = 12345
        form_manager.start_add_card_form(user_id)
        
        # Add some data
        form_manager.update_form_field(user_id, "bank_name", "HDFC")
        
        # Clear form
        form_manager.clear_form(user_id)
        
        # Form data should be gone
        form_data = form_manager.get_form_data(user_id)
        assert form_data is None
        
        # Session should be gone
        session = form_manager.db_manager.get_user_session(user_id)
        assert session is None
    
    def test_validate_card_number_last_4(self, form_manager):
        """Test card number validation for last 4 digits."""
        assert form_manager.validate_card_number("1234") is True
        assert form_manager.validate_card_number("5678") is True
        assert form_manager.validate_card_number("0000") is True
    
    def test_validate_card_number_full(self, form_manager):
        """Test card number validation for full card numbers."""
        assert form_manager.validate_card_number("1234567890123456") is True  # 16 digits
        assert form_manager.validate_card_number("123456789012345") is True   # 15 digits
        assert form_manager.validate_card_number("1234567890123456789") is True  # 19 digits
    
    def test_validate_card_number_invalid(self, form_manager):
        """Test card number validation for invalid numbers."""
        assert form_manager.validate_card_number("123") is False  # Too short
        assert form_manager.validate_card_number("12345") is False  # 5 digits
        assert form_manager.validate_card_number("abc1234") is False  # Non-digits
        assert form_manager.validate_card_number("12345678901234567890") is False  # Too long
    
    def test_validate_card_number_with_spaces(self, form_manager):
        """Test card number validation with spaces and dashes."""
        assert form_manager.validate_card_number("1234 5678 9012 3456") is True
        assert form_manager.validate_card_number("1234-5678-9012-3456") is True
        assert form_manager.validate_card_number("123 4567 8901 2345") is True
    
    def test_validate_expiry_date_valid(self, form_manager):
        """Test expiry date validation for valid dates."""
        assert form_manager.validate_expiry_date("01/2025") is True
        assert form_manager.validate_expiry_date("12/2030") is True
        assert form_manager.validate_expiry_date("06/2023") is True
    
    def test_validate_expiry_date_invalid(self, form_manager):
        """Test expiry date validation for invalid dates."""
        assert form_manager.validate_expiry_date("13/2025") is False  # Invalid month
        assert form_manager.validate_expiry_date("00/2025") is False  # Invalid month
        assert form_manager.validate_expiry_date("12/2019") is False  # Past year
        assert form_manager.validate_expiry_date("12/2031") is False  # Too far future
        assert form_manager.validate_expiry_date("12-2025") is False  # Wrong separator
        assert form_manager.validate_expiry_date("2025/12") is False  # Wrong format
        assert form_manager.validate_expiry_date("abc") is False  # Invalid format
    
    def test_validate_cvv_valid(self, form_manager):
        """Test CVV validation for valid CVVs."""
        assert form_manager.validate_cvv("123") is True  # 3 digits
        assert form_manager.validate_cvv("1234") is True  # 4 digits
        assert form_manager.validate_cvv("000") is True
        assert form_manager.validate_cvv("9999") is True
    
    def test_validate_cvv_invalid(self, form_manager):
        """Test CVV validation for invalid CVVs."""
        assert form_manager.validate_cvv("12") is False  # Too short
        assert form_manager.validate_cvv("12345") is False  # Too long
        assert form_manager.validate_cvv("abc") is False  # Non-digits
        assert form_manager.validate_cvv("12a") is False  # Mixed 