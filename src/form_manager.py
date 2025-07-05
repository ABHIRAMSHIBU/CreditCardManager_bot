"""
Credit Card Management Bot - Form Manager Module
Form state management for credit card operations.

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

import json
import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class FormState(Enum):
    """Enum for form states."""
    IDLE = "idle"
    WAITING_BANK_NAME = "waiting_bank_name"
    WAITING_CARD_NUMBER = "waiting_card_number"
    WAITING_EXPIRY_DATE = "waiting_expiry_date"
    WAITING_CVV = "waiting_cvv"
    WAITING_BILLING_DATE = "waiting_billing_date"
    WAITING_BILL_AMOUNT = "waiting_bill_amount"
    WAITING_GRACE_DAYS = "waiting_grace_days"

class FormManager:
    """Manages form state for credit card addition."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def start_add_card_form(self, user_id: int) -> Dict[str, Any]:
        """Start a new add card form for a user."""
        form_data = {
            "bank_name": "",
            "card_number": "",
            "expiry_date": "",
            "cvv": "",
            "full_card_number": ""
        }
        
        self.db_manager.save_user_session(user_id, FormState.IDLE.value, json.dumps(form_data))
        return form_data
    
    def get_form_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get current form data for a user."""
        session = self.db_manager.get_user_session(user_id)
        if session and session.get('form_data'):
            try:
                return json.loads(session['form_data'])
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in form data for user {user_id}")
                return None
        return None
    
    def get_current_state(self, user_id: int) -> FormState:
        """Get current form state for a user."""
        session = self.db_manager.get_user_session(user_id)
        if session and session.get('current_state'):
            try:
                return FormState(session['current_state'])
            except ValueError:
                logger.error(f"Invalid state for user {user_id}: {session['current_state']}")
                return FormState.IDLE
        return FormState.IDLE
    
    def set_state(self, user_id: int, state: FormState):
        """Set form state for a user."""
        form_data = self.get_form_data(user_id) or {}
        self.db_manager.save_user_session(user_id, state.value, json.dumps(form_data))
    
    def update_form_field(self, user_id: int, field: str, value: str) -> bool:
        """Update a specific field in the form data."""
        form_data = self.get_form_data(user_id)
        if form_data is None:
            return False
        
        form_data[field] = value
        current_state = self.get_current_state(user_id)
        self.db_manager.save_user_session(user_id, current_state.value, json.dumps(form_data))
        return True
    
    def is_form_complete(self, user_id: int) -> bool:
        """Check if the form is complete and ready to save."""
        form_data = self.get_form_data(user_id)
        if not form_data:
            return False
        
        # Check required fields
        required_fields = ["bank_name", "card_number", "expiry_date"]
        for field in required_fields:
            if not form_data.get(field):
                return False
        
        # If full card number is provided, CVV is required
        if form_data.get("full_card_number") and not form_data.get("cvv"):
            return False
        
        return True
    
    def clear_form(self, user_id: int):
        """Clear the form data for a user."""
        self.db_manager.clear_user_session(user_id)
    
    def validate_card_number(self, card_number: str) -> bool:
        """Validate card number format."""
        # Check if the input contains only digits, spaces, and dashes
        allowed_chars = set('0123456789 -')
        if not all(c in allowed_chars for c in card_number):
            return False
        
        # Remove spaces and dashes
        cleaned = ''.join(filter(str.isdigit, card_number))
        
        # Check if it's 4 digits (last 4) or 13-19 digits (full number)
        if len(cleaned) == 4:
            return True
        elif 13 <= len(cleaned) <= 19:
            return True
        return False
    
    def validate_expiry_date(self, expiry_date: str) -> bool:
        """Validate expiry date format (MM/YYYY)."""
        try:
            if '/' not in expiry_date:
                return False
            
            month, year = expiry_date.split('/')
            month = int(month)
            year = int(year)
            
            if not (1 <= month <= 12):
                return False
            
            if not (2020 <= year <= 2030):
                return False
            
            return True
        except (ValueError, IndexError):
            return False
    
    def validate_cvv(self, cvv: str) -> bool:
        """Validate CVV format."""
        if not cvv.isdigit():
            return False
        
        return 3 <= len(cvv) <= 4
    
    def validate_billing_date(self, billing_date: str) -> bool:
        """Validate billing date format (1-31)."""
        try:
            day = int(billing_date)
            return 1 <= day <= 31
        except ValueError:
            return False
    
    def validate_bill_amount(self, amount: str) -> bool:
        """Validate bill amount format."""
        try:
            # Remove currency symbols and commas
            cleaned = amount.replace('$', '').replace(',', '').replace(' ', '')
            value = float(cleaned)
            return value > 0
        except ValueError:
            return False
    
    def validate_grace_days(self, grace_days: str) -> bool:
        """Validate payment grace days format."""
        try:
            days = int(grace_days)
            return 1 <= days <= 60  # Reasonable range: 1-60 days
        except ValueError:
            return False 