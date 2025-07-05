"""
Credit Card Management Bot - Handlers Module
Command and callback handlers for the credit card bot.

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

import logging
from typing import Dict, Any, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .database import DatabaseManager
from .form_manager import FormManager, FormState
import json

logger = logging.getLogger(__name__)

class CreditCardHandlers:
    """Handlers for credit card management commands."""
    
    def __init__(self, db_manager: DatabaseManager, form_manager: FormManager):
        self.db_manager = db_manager
        self.form_manager = form_manager
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        if not user:
            return
        
        welcome_message = (
            f"Hello {user.first_name}! 👋\n\n"
            "Welcome to your Credit Card Manager Bot! 💳\n\n"
            "Available commands:\n"
            "/add_card - Add a new credit card\n"
            "/view_cards - View all your credit cards\n"
            "/view_card <search> - View a specific card\n"
            "/delete_card <search> - Delete a credit card\n"
            "/status - Show status of all cards and bills\n"
            "/set_billing - Set billing information for a card\n"
            "/update_bill_amount - Update bill amount for a card\n"
            "/set_due_date - Set payment grace period for a card\n"
            "/help - Show this help message\n\n"
            "**New Billing Features:**\n"
            "• Set billing dates and amounts\n"
            "• Get notifications for due bills\n"
            "• Mark bills as paid\n"
            "• Track payment status\n\n"
            "Your data is completely private and isolated to your account only! 🔒"
        )
        
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = (
            "📋 **Credit Card Manager Bot Commands**\n\n"
            "**Basic Commands:**\n"
            "• `/add_card` - Add a new credit card with interactive form\n"
            "• `/view_cards` - View all your credit cards\n"
            "• `/view_card <bank_name or last_4_digits>` - View specific card\n"
            "• `/delete_card <bank_name or last_4_digits>` - Delete a card\n"
            "• `/status` - Show status of all cards and bills\n"
            "• `/set_billing` - Set billing information for a card\n"
            "• `/update_bill_amount` - Update bill amount for a card\n"
            "• `/set_due_date` - Set payment grace period for a card\n"
            "• `/help` - Show this help message\n\n"
            "**Examples:**\n"
            "• `/view_card HDFC` - View HDFC card\n"
            "• `/view_card 1234` - View card ending with 1234\n"
            "• `/delete_card 5678` - Delete card ending with 5678\n\n"
            "**Billing Features:**\n"
            "• Set billing date and amount for each card\n"
            "• Set payment grace period (due date) for each card\n"
            "• Update bill amounts when new bills are generated\n"
            "• Get notifications for due bills\n"
            "• Mark bills as paid to update next due date\n"
            "• View status of all pending and due bills\n\n"
            "🔒 **Security:** Your data is encrypted and isolated per user!"
        )
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def add_card_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /add_card command."""
        user = update.effective_user
        if not user:
            return
        
        # Start the form
        form_data = self.form_manager.start_add_card_form(user.id)
        
        # Create inline keyboard for form fields
        keyboard = [
            [
                InlineKeyboardButton("🏦 Bank Name", callback_data="form_field_bank_name"),
                InlineKeyboardButton("💳 Card Number", callback_data="form_field_card_number")
            ],
            [
                InlineKeyboardButton("📅 Expiry Date", callback_data="form_field_expiry_date"),
                InlineKeyboardButton("🔐 CVV", callback_data="form_field_cvv")
            ],
            [
                InlineKeyboardButton("✅ Done", callback_data="form_done"),
                InlineKeyboardButton("❌ Cancel", callback_data="form_cancel")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "💳 **Add New Credit Card**\n\n"
            "Please fill in the card details. Click on the buttons below to fill each field:\n\n"
            f"🏦 **Bank Name:** {form_data['bank_name'] or 'Not set'}\n"
            f"💳 **Card Number:** {form_data['card_number'] or 'Not set'}\n"
            f"📅 **Expiry Date:** {form_data['expiry_date'] or 'Not set'}\n"
            f"🔐 **CVV:** {form_data['cvv'] or 'Not set'}\n\n"
            "Click 'Done' when you're finished!"
        )
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def view_cards_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /view_cards command."""
        user = update.effective_user
        if not user:
            return
        
        cards = self.db_manager.get_user_cards(user.id)
        
        if not cards:
            await update.message.reply_text(
                "📭 You don't have any credit cards saved yet.\n"
                "Use `/add_card` to add your first card!",
                parse_mode='Markdown'
            )
            return
        
        # Create inline keyboard with card options
        keyboard = []
        for card in cards:
            bank_short = card['bank_name'][:4].upper()
            card_short = card['card_number'][-4:] if len(card['card_number']) >= 4 else card['card_number']
            button_text = f"{bank_short} •••• {card_short}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"view_card_{card['id']}")])
        
        keyboard.append([InlineKeyboardButton("❌ Close", callback_data="close_view")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"💳 **Your Credit Cards** ({len(cards)})\n\n"
            "Select a card to view details:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def view_card_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /view_card command with search term."""
        user = update.effective_user
        if not user:
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a search term.\n"
                "Usage: `/view_card <bank_name or last_4_digits>`",
                parse_mode='Markdown'
            )
            return
        
        search_term = context.args[0]
        cards = self.db_manager.get_cards_by_bank_or_number(user.id, search_term)
        
        if not cards:
            await update.message.reply_text(
                f"❌ No cards found matching '{search_term}'.\n"
                "Try using `/view_cards` to see all your cards.",
                parse_mode='Markdown'
            )
            return
        
        if len(cards) == 1:
            # Show single card directly
            await self._show_card_details(update, cards[0])
        else:
            # Show selection menu for multiple cards
            keyboard = []
            for card in cards:
                bank_short = card['bank_name'][:4].upper()
                card_short = card['card_number'][-4:] if len(card['card_number']) >= 4 else card['card_number']
                button_text = f"{bank_short} •••• {card_short}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"view_card_{card['id']}")])
            
            keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="close_view")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🔍 **Multiple cards found for '{search_term}'**\n\n"
                "Select a card to view details:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def delete_card_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /delete_card command with search term."""
        user = update.effective_user
        if not user:
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a search term.\n"
                "Usage: `/delete_card <bank_name or last_4_digits>`",
                parse_mode='Markdown'
            )
            return
        
        search_term = context.args[0]
        cards = self.db_manager.get_cards_by_bank_or_number(user.id, search_term)
        
        if not cards:
            await update.message.reply_text(
                f"❌ No cards found matching '{search_term}'.\n"
                "Try using `/view_cards` to see all your cards.",
                parse_mode='Markdown'
            )
            return
        
        if len(cards) == 1:
            # Show single card with delete option
            await self._show_card_for_deletion(update, cards[0])
        else:
            # Show selection menu for multiple cards
            keyboard = []
            for card in cards:
                bank_short = card['bank_name'][:4].upper()
                card_short = card['card_number'][-4:] if len(card['card_number']) >= 4 else card['card_number']
                button_text = f"{bank_short} •••• {card_short}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"delete_card_{card['id']}")])
            
            keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="close_view")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🗑️ **Multiple cards found for '{search_term}'**\n\n"
                "Select a card to delete:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards."""
        query = update.callback_query
        user = update.effective_user
        if not user or not query:
            return
        
        await query.answer()
        
        if query.data.startswith("form_field_"):
            await self._handle_form_field_callback(query, user.id)
        elif query.data.startswith("view_card_"):
            await self._handle_view_card_callback(query, user.id)
        elif query.data.startswith("delete_card_"):
            await self._handle_delete_card_callback(query, user.id)
        elif query.data.startswith("confirm_delete_"):
            await self._handle_confirm_delete_callback(query, user.id)
        elif query.data.startswith("mark_paid_"):
            await self._handle_mark_paid_callback(query, user.id)
        elif query.data.startswith("set_billing_"):
            await self._handle_set_billing_callback(query, user.id)
        elif query.data.startswith("update_amount_"):
            await self._handle_update_amount_callback(query, user.id)
        elif query.data.startswith("set_grace_days_"):
            await self._handle_set_grace_days_callback(query, user.id)
        elif query.data == "view_due_bills":
            await self._handle_view_due_bills_callback(query, user.id)
        elif query.data == "view_pending_bills":
            await self._handle_view_pending_bills_callback(query, user.id)
        elif query.data == "view_all_cards":
            await self._handle_view_all_cards_callback(query, user.id)
        elif query.data == "form_done":
            await self._handle_form_done(query, user.id)
        elif query.data == "form_cancel":
            await self._handle_form_cancel(query, user.id)
        elif query.data == "close_view":
            await query.edit_message_text("❌ View closed.")
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages for form input."""
        user = update.effective_user
        if not user:
            return
        
        current_state = self.form_manager.get_current_state(user.id)
        text = update.message.text
        
        if current_state == FormState.IDLE:
            # Not in form mode, ignore
            return
        
        # Handle form input based on current state
        if current_state == FormState.WAITING_BANK_NAME:
            if len(text) < 2:
                await update.message.reply_text("❌ Bank name must be at least 2 characters long.")
                return
            
            self.form_manager.update_form_field(user.id, "bank_name", text)
            self.form_manager.set_state(user.id, FormState.IDLE)
            await self._show_form_status(update, user.id)
            
        elif current_state == FormState.WAITING_CARD_NUMBER:
            if not self.form_manager.validate_card_number(text):
                await update.message.reply_text(
                    "❌ Invalid card number format.\n"
                    "Please enter either:\n"
                    "• Last 4 digits (e.g., 1234)\n"
                    "• Full card number (13-19 digits)"
                )
                return
            
            # Determine if it's full card number or last 4 digits
            cleaned = ''.join(filter(str.isdigit, text))
            if len(cleaned) == 4:
                self.form_manager.update_form_field(user.id, "card_number", cleaned)
            else:
                self.form_manager.update_form_field(user.id, "card_number", cleaned[-4:])
                self.form_manager.update_form_field(user.id, "full_card_number", cleaned)
            
            self.form_manager.set_state(user.id, FormState.IDLE)
            await self._show_form_status(update, user.id)
            
        elif current_state == FormState.WAITING_EXPIRY_DATE:
            if not self.form_manager.validate_expiry_date(text):
                await update.message.reply_text(
                    "❌ Invalid expiry date format.\n"
                    "Please use MM/YYYY format (e.g., 12/2025)"
                )
                return
            
            self.form_manager.update_form_field(user.id, "expiry_date", text)
            self.form_manager.set_state(user.id, FormState.IDLE)
            await self._show_form_status(update, user.id)
            
        elif current_state == FormState.WAITING_CVV:
            if not self.form_manager.validate_cvv(text):
                await update.message.reply_text(
                    "❌ Invalid CVV format.\n"
                    "CVV must be 3-4 digits."
                )
                return
            
            self.form_manager.update_form_field(user.id, "cvv", text)
            self.form_manager.set_state(user.id, FormState.IDLE)
            await self._show_form_status(update, user.id)
        
        elif current_state == FormState.WAITING_BILLING_DATE:
            if not self.form_manager.validate_billing_date(text):
                await update.message.reply_text(
                    "❌ Invalid billing date format.\n"
                    "Please enter a day of the month (1-31)."
                )
                return
            
            self.form_manager.update_form_field(user.id, "billing_date", text)
            self.form_manager.set_state(user.id, FormState.WAITING_BILL_AMOUNT)
            await update.message.reply_text("💰 Please enter the bill amount (e.g., 150.00):")
        
        elif current_state == FormState.WAITING_BILL_AMOUNT:
            if not self.form_manager.validate_bill_amount(text):
                await update.message.reply_text(
                    "❌ Invalid amount format.\n"
                    "Please enter a valid amount (e.g., 150.00 or $150)."
                )
                return
            
            # Clean the amount
            cleaned_amount = text.replace('$', '').replace(',', '').replace(' ', '')
            self.form_manager.update_form_field(user.id, "bill_amount", cleaned_amount)
            self.form_manager.set_state(user.id, FormState.IDLE)
            await self._handle_billing_form_done(update, user.id)
        
        elif current_state == FormState.WAITING_GRACE_DAYS:
            if not self.form_manager.validate_grace_days(text):
                await update.message.reply_text(
                    "❌ Invalid grace days format.\n"
                    "Please enter a number between 1 and 60 days."
                )
                return
            
            self.form_manager.update_form_field(user.id, "grace_days", text)
            self.form_manager.set_state(user.id, FormState.IDLE)
            await self._handle_grace_days_form_done(update, user.id)
    
    async def _handle_form_field_callback(self, query, user_id: int):
        """Handle form field button callbacks."""
        field = query.data.replace("form_field_", "")
        
        if field == "bank_name":
            self.form_manager.set_state(user_id, FormState.WAITING_BANK_NAME)
            await query.edit_message_text("🏦 Please enter the bank name:")
            
        elif field == "card_number":
            self.form_manager.set_state(user_id, FormState.WAITING_CARD_NUMBER)
            await query.edit_message_text(
                "💳 Please enter the card number:\n\n"
                "You can enter:\n"
                "• Last 4 digits (e.g., 1234)\n"
                "• Full card number (13-19 digits)"
            )
            
        elif field == "expiry_date":
            self.form_manager.set_state(user_id, FormState.WAITING_EXPIRY_DATE)
            await query.edit_message_text("📅 Please enter the expiry date (MM/YYYY):")
            
        elif field == "cvv":
            self.form_manager.set_state(user_id, FormState.WAITING_CVV)
            await query.edit_message_text("🔐 Please enter the CVV (3-4 digits):")
    
    async def _handle_form_done(self, query, user_id: int):
        """Handle form completion."""
        if not self.form_manager.is_form_complete(user_id):
            await query.edit_message_text(
                "❌ Form is not complete!\n\n"
                "Please fill in all required fields:\n"
                "• Bank Name\n"
                "• Card Number\n"
                "• Expiry Date\n\n"
                "CVV is required if you provided a full card number."
            )
            return
        
        form_data = self.form_manager.get_form_data(user_id)
        
        # Save the card
        success = self.db_manager.add_credit_card(
            user_id=user_id,
            bank_name=form_data['bank_name'],
            card_number=form_data['card_number'],
            expiry_date=form_data['expiry_date'],
            cvv=form_data.get('cvv'),
            full_card_number=form_data.get('full_card_number')
        )
        
        if success:
            await query.edit_message_text(
                "✅ **Credit card added successfully!**\n\n"
                f"🏦 **Bank:** {form_data['bank_name']}\n"
                f"💳 **Card:** •••• {form_data['card_number']}\n"
                f"📅 **Expires:** {form_data['expiry_date']}\n\n"
                "Your card has been saved securely! 🔒"
            )
            self.form_manager.clear_form(user_id)
        else:
            await query.edit_message_text(
                "❌ **Failed to add credit card!**\n\n"
                "This card might already exist in your account."
            )
    
    async def _handle_form_cancel(self, query, user_id: int):
        """Handle form cancellation."""
        self.form_manager.clear_form(user_id)
        await query.edit_message_text("❌ Form cancelled. No data was saved.")
    
    async def _show_form_status(self, update: Update, user_id: int):
        """Show current form status."""
        form_data = self.form_manager.get_form_data(user_id)
        if not form_data:
            return
        
        keyboard = [
            [
                InlineKeyboardButton("🏦 Bank Name", callback_data="form_field_bank_name"),
                InlineKeyboardButton("💳 Card Number", callback_data="form_field_card_number")
            ],
            [
                InlineKeyboardButton("📅 Expiry Date", callback_data="form_field_expiry_date"),
                InlineKeyboardButton("🔐 CVV", callback_data="form_field_cvv")
            ],
            [
                InlineKeyboardButton("✅ Done", callback_data="form_done"),
                InlineKeyboardButton("❌ Cancel", callback_data="form_cancel")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "💳 **Add New Credit Card**\n\n"
            "Please fill in the card details. Click on the buttons below to fill each field:\n\n"
            f"🏦 **Bank Name:** {form_data['bank_name'] or 'Not set'}\n"
            f"💳 **Card Number:** {form_data['card_number'] or 'Not set'}\n"
            f"📅 **Expiry Date:** {form_data['expiry_date'] or 'Not set'}\n"
            f"🔐 **CVV:** {form_data['cvv'] or 'Not set'}\n\n"
            "Click 'Done' when you're finished!"
        )
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _handle_view_card_callback(self, query, user_id: int):
        """Handle view card callback."""
        card_id = int(query.data.replace("view_card_", ""))
        card = self.db_manager.get_card_by_id(user_id, card_id)
        
        if not card:
            await query.edit_message_text("❌ Card not found!")
            return
        
        await self._show_card_details_from_query(query, card)
    
    async def _handle_delete_card_callback(self, query, user_id: int):
        """Handle delete card callback."""
        card_id = int(query.data.replace("delete_card_", ""))
        card = self.db_manager.get_card_by_id(user_id, card_id)
        
        if not card:
            await query.edit_message_text("❌ Card not found!")
            return
        
        await self._show_card_for_deletion_from_query(query, card)
    
    async def _handle_confirm_delete_callback(self, query, user_id: int):
        """Handle confirm delete callback."""
        card_id = int(query.data.replace("confirm_delete_", ""))
        card = self.db_manager.get_card_by_id(user_id, card_id)
        
        if not card:
            await query.edit_message_text("❌ Card not found!")
            return
        
        # Delete the card
        success = self.db_manager.delete_card(user_id, card_id)
        
        if success:
            await query.edit_message_text(
                f"✅ **Card deleted successfully!**\n\n"
                f"🏦 **Bank:** {card['bank_name']}\n"
                f"💳 **Card:** •••• {card['card_number']}\n\n"
                "The card has been permanently removed from your account."
            )
        else:
            await query.edit_message_text("❌ Failed to delete card!")
    
    async def _handle_mark_paid_callback(self, query, user_id: int):
        """Handle mark bill as paid callback."""
        card_id = int(query.data.replace("mark_paid_", ""))
        card = self.db_manager.get_card_by_id(user_id, card_id)
        
        if not card:
            await query.edit_message_text("❌ Card not found!")
            return
        
        # Mark bill as paid
        success = self.db_manager.mark_bill_paid(user_id, card_id)
        
        if success:
            await query.edit_message_text(
                f"✅ **Bill marked as paid!**\n\n"
                f"🏦 **Bank:** {card['bank_name']}\n"
                f"💳 **Card:** •••• {card['card_number']}\n\n"
                "Next bill date has been updated automatically."
            )
        else:
            await query.edit_message_text("❌ Failed to mark bill as paid!")
    
    async def _handle_set_billing_callback(self, query, user_id: int):
        """Handle set billing callback."""
        card_id = int(query.data.replace("set_billing_", ""))
        card = self.db_manager.get_card_by_id(user_id, card_id)
        
        if not card:
            await query.edit_message_text("❌ Card not found!")
            return
        
        # Start billing form
        form_data = {"card_id": card_id}
        self.form_manager.db_manager.save_user_session(user_id, FormState.WAITING_BILLING_DATE.value, json.dumps(form_data))
        
        await query.edit_message_text(
            f"💳 **Set Billing for {card['bank_name']}**\n\n"
            "📅 Please enter the billing date (day of month, 1-31):"
        )
    
    async def _handle_update_amount_callback(self, query, user_id: int):
        """Handle update amount callback."""
        card_id = int(query.data.replace("update_amount_", ""))
        card = self.db_manager.get_card_by_id(user_id, card_id)
        
        if not card:
            await query.edit_message_text("❌ Card not found!")
            return
        
        # Start billing form
        form_data = {"card_id": card_id}
        self.form_manager.db_manager.save_user_session(user_id, FormState.WAITING_BILL_AMOUNT.value, json.dumps(form_data))
        
        await query.edit_message_text(
            f"💰 **Update Bill Amount for {card['bank_name']}**\n\n"
            "Please enter the new bill amount (e.g., 150.00):"
        )
    
    async def _handle_set_grace_days_callback(self, query, user_id: int):
        """Handle set grace days callback."""
        card_id = int(query.data.replace("set_grace_days_", ""))
        card = self.db_manager.get_card_by_id(user_id, card_id)
        
        if not card:
            await query.edit_message_text("❌ Card not found!")
            return
        
        # Start grace days form
        form_data = {"card_id": card_id}
        self.form_manager.db_manager.save_user_session(user_id, FormState.WAITING_GRACE_DAYS.value, json.dumps(form_data))
        
        await query.edit_message_text(
            f"📅 **Set Payment Due Date for {card['bank_name']}**\n\n"
            "Please enter the number of days after billing date when payment is due (e.g., 21):"
        )
    
    async def _handle_view_due_bills_callback(self, query, user_id: int):
        """Handle view due bills callback."""
        due_bills = self.db_manager.get_due_bills(user_id)
        
        if not due_bills:
            await query.edit_message_text("✅ No due bills found!")
            return
        
        message = "🚨 **DUE/OVERDUE BILLS:**\n\n"
        keyboard = []
        
        for card in due_bills:
            days_overdue = 0
            if card['next_bill_date']:
                from datetime import datetime
                due_date = datetime.strptime(card['next_bill_date'], '%Y-%m-%d')
                days_overdue = (datetime.now() - due_date).days
            
            message += f"⚠️ **{card['bank_name']}** (••••{card['card_number']})\n"
            message += f"   Due: {card['next_bill_date']}"
            if days_overdue > 0:
                message += f" ({days_overdue} days overdue)"
            if card['bill_amount']:
                message += f"\n   Amount: ${card['bill_amount']}"
            message += "\n\n"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"✅ Mark Paid - {card['bank_name']}", 
                    callback_data=f"mark_paid_{card['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("❌ Close", callback_data="close_view")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _handle_view_pending_bills_callback(self, query, user_id: int):
        """Handle view pending bills callback."""
        pending_bills = self.db_manager.get_pending_bills(user_id)
        
        if not pending_bills:
            await query.edit_message_text("✅ No pending bills found!")
            return
        
        message = "📅 **PENDING BILLS:**\n\n"
        keyboard = []
        
        for card in pending_bills:
            message += f"📋 **{card['bank_name']}** (••••{card['card_number']})\n"
            message += f"   Due: {card['next_bill_date']}"
            if card['bill_amount']:
                message += f"\n   Amount: ${card['bill_amount']}"
            message += "\n\n"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"✅ Mark Paid - {card['bank_name']}", 
                    callback_data=f"mark_paid_{card['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("❌ Close", callback_data="close_view")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _handle_view_all_cards_callback(self, query, user_id: int):
        """Handle view all cards callback."""
        cards = self.db_manager.get_user_cards(user_id)
        
        if not cards:
            await query.edit_message_text("❌ No cards found!")
            return
        
        message = "💳 **Your Credit Cards:**\n\n"
        keyboard = []
        
        for card in cards:
            message += f"🏦 **{card['bank_name']}** (••••{card['card_number']})\n"
            message += f"   Expires: {card['expiry_date']}\n"
            if card.get('next_bill_date'):
                message += f"   Next Bill: {card['next_bill_date']}\n"
            if card.get('bill_amount'):
                message += f"   Amount: ${card['bill_amount']}\n"
            message += "\n"
            
            keyboard.append([
                InlineKeyboardButton(
                    f"👁️ View - {card['bank_name']}", 
                    callback_data=f"view_card_{card['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("❌ Close", callback_data="close_view")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _handle_billing_form_done(self, update: Update, user_id: int):
        """Handle billing form completion."""
        form_data = self.form_manager.get_form_data(user_id)
        if not form_data or not form_data.get('bill_amount'):
            await update.message.reply_text("❌ Bill amount is required!")
            return
        
        # Get the card ID from form data
        card_id = form_data.get('card_id')
        if not card_id:
            await update.message.reply_text("❌ Card not found!")
            return
        
        # Check if this is updating amount only or setting full billing info
        if form_data.get('billing_date'):
            # Setting full billing information
            success = self.db_manager.update_billing_info(
                user_id, 
                card_id, 
                int(form_data['billing_date']), 
                float(form_data['bill_amount'])
            )
            
            if success:
                await update.message.reply_text(
                    "✅ **Billing information updated successfully!**\n\n"
                    f"📅 **Billing Date:** {form_data['billing_date']}th of each month\n"
                    f"💰 **Bill Amount:** ${form_data['bill_amount']}\n\n"
                    "You'll receive notifications when bills are due!"
                )
            else:
                await update.message.reply_text("❌ Failed to update billing information!")
        else:
            # Updating amount only
            success = self.db_manager.update_bill_amount(
                user_id, 
                card_id, 
                float(form_data['bill_amount'])
            )
            
            if success:
                await update.message.reply_text(
                    "✅ **Bill amount updated successfully!**\n\n"
                    f"💰 **New Amount:** ${form_data['bill_amount']}\n\n"
                    "The bill amount has been updated for this card."
                )
            else:
                await update.message.reply_text("❌ Failed to update bill amount!")
        
        self.form_manager.clear_form(user_id)
    
    async def _handle_grace_days_form_done(self, update: Update, user_id: int):
        """Handle grace days form completion."""
        form_data = self.form_manager.get_form_data(user_id)
        if not form_data or not form_data.get('grace_days'):
            await update.message.reply_text("❌ Grace days is required!")
            return
        
        # Get the card ID from form data
        card_id = form_data.get('card_id')
        if not card_id:
            await update.message.reply_text("❌ Card not found!")
            return
        
        # Update grace days
        success = self.db_manager.update_payment_grace_days(
            user_id, 
            card_id, 
            int(form_data['grace_days'])
        )
        
        if success:
            await update.message.reply_text(
                "✅ **Payment due date updated successfully!**\n\n"
                f"📅 **Grace Period:** {form_data['grace_days']} days after billing date\n\n"
                "This will be used to calculate accurate due dates for future bills."
            )
        else:
            await update.message.reply_text("❌ Failed to update payment due date!")
        
        self.form_manager.clear_form(user_id)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show status of all cards and bills."""
        user = update.effective_user
        if not user:
            return
        
        # Get all cards
        cards = self.db_manager.get_user_cards(user.id)
        if not cards:
            await update.message.reply_text(
                "📊 **Status Report**\n\n"
                "You don't have any credit cards added yet.\n"
                "Use /add_card to add your first card!"
            )
            return
        
        # Get pending and due bills
        pending_bills = self.db_manager.get_pending_bills(user.id)
        due_bills = self.db_manager.get_due_bills(user.id)
        
        message = "📊 **Credit Card Status Report**\n\n"
        
        # Summary
        total_cards = len(cards)
        total_pending = len(pending_bills)
        total_due = len(due_bills)
        
        message += f"📈 **Summary:**\n"
        message += f"• Total Cards: {total_cards}\n"
        message += f"• Pending Bills: {total_pending}\n"
        message += f"• Due/Overdue: {total_due}\n\n"
        
        if due_bills:
            message += "🚨 **DUE/OVERDUE BILLS:**\n"
            for card in due_bills:
                days_overdue = 0
                if card['next_bill_date']:
                    from datetime import datetime
                    due_date = datetime.strptime(card['next_bill_date'], '%Y-%m-%d')
                    days_overdue = (datetime.now() - due_date).days
                
                message += f"⚠️ **{card['bank_name']}** (••••{card['card_number']})\n"
                message += f"   Due: {card['next_bill_date']}"
                if days_overdue > 0:
                    message += f" ({days_overdue} days overdue)"
                if card['bill_amount']:
                    message += f"\n   Amount: ${card['bill_amount']}"
                message += "\n\n"
        
        if pending_bills and not due_bills:
            message += "📅 **UPCOMING BILLS:**\n"
            for card in pending_bills[:5]:  # Show only next 5
                message += f"📋 **{card['bank_name']}** (••••{card['card_number']})\n"
                message += f"   Due: {card['next_bill_date']}"
                if card['bill_amount']:
                    message += f"\n   Amount: ${card['bill_amount']}"
                message += "\n\n"
        
        # Add action buttons
        keyboard = []
        if due_bills:
            keyboard.append([InlineKeyboardButton("🚨 View Due Bills", callback_data="view_due_bills")])
        if pending_bills:
            keyboard.append([InlineKeyboardButton("📅 View All Pending", callback_data="view_pending_bills")])
        keyboard.append([InlineKeyboardButton("💳 View All Cards", callback_data="view_all_cards")])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def set_billing_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set billing information for a card."""
        user = update.effective_user
        if not user:
            return
        
        # Get user's cards
        cards = self.db_manager.get_user_cards(user.id)
        if not cards:
            await update.message.reply_text(
                "❌ You don't have any credit cards added yet.\n"
                "Use /add_card to add your first card!"
            )
            return
        
        # Show card selection
        keyboard = []
        for card in cards:
            keyboard.append([
                InlineKeyboardButton(
                    f"{card['bank_name']} (••••{card['card_number']})", 
                    callback_data=f"set_billing_{card['id']}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "💳 **Set Billing Information**\n\n"
            "Select a card to set billing information:",
            reply_markup=reply_markup
        )
    
    async def update_bill_amount_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Update bill amount for a card."""
        user = update.effective_user
        if not user:
            return
        
        # Get user's cards that have billing information
        cards = self.db_manager.get_user_cards(user.id)
        if not cards:
            await update.message.reply_text(
                "❌ You don't have any credit cards added yet.\n"
                "Use /add_card to add your first card!"
            )
            return
        
        # Filter cards that have billing information
        cards_with_billing = [card for card in cards if card.get('billing_date') is not None]
        
        if not cards_with_billing:
            await update.message.reply_text(
                "❌ None of your cards have billing information set.\n"
                "Use /set_billing to set billing information first!"
            )
            return
        
        # Show card selection
        keyboard = []
        for card in cards_with_billing:
            current_amount = card.get('bill_amount', 'Not set')
            keyboard.append([
                InlineKeyboardButton(
                    f"{card['bank_name']} (••••{card['card_number']}) - ${current_amount}", 
                    callback_data=f"update_amount_{card['id']}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "💰 **Update Bill Amount**\n\n"
            "Select a card to update its bill amount:",
            reply_markup=reply_markup
        )
    
    async def set_due_date_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set payment grace days (due date) for a card."""
        user = update.effective_user
        if not user:
            return
        
        # Get user's cards that have billing information
        cards = self.db_manager.get_user_cards(user.id)
        if not cards:
            await update.message.reply_text(
                "❌ You don't have any credit cards added yet.\n"
                "Use /add_card to add your first card!"
            )
            return
        
        # Filter cards that have billing information
        cards_with_billing = [card for card in cards if card.get('billing_date') is not None]
        
        if not cards_with_billing:
            await update.message.reply_text(
                "❌ None of your cards have billing information set.\n"
                "Use /set_billing to set billing information first!"
            )
            return
        
        # Show card selection
        keyboard = []
        for card in cards_with_billing:
            current_grace_days = card.get('payment_grace_days', 21)
            keyboard.append([
                InlineKeyboardButton(
                    f"{card['bank_name']} (••••{card['card_number']}) - {current_grace_days} days", 
                    callback_data=f"set_grace_days_{card['id']}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📅 **Set Payment Due Date**\n\n"
            "Select a card to set payment grace days (how many days after billing date the payment is due):",
            reply_markup=reply_markup
        )
    
    async def _show_card_details(self, update: Update, card: Dict[str, Any]):
        """Show card details."""
        message = (
            f"💳 **{card['bank_name']} Credit Card**\n\n"
            f"🏦 **Bank:** {card['bank_name']}\n"
            f"💳 **Card Number:** •••• {card['card_number']}\n"
            f"📅 **Expiry Date:** {card['expiry_date']}\n"
        )
        
        if card.get('cvv'):
            message += f"🔐 **CVV:** {card['cvv']}\n"
        
        if card.get('full_card_number'):
            message += f"🔢 **Full Number:** {card['full_card_number']}\n"
        
        message += f"\n📅 **Added:** {card['created_at']}"
        
        keyboard = [
            [InlineKeyboardButton("🗑️ Delete Card", callback_data=f"confirm_delete_{card['id']}")],
            [InlineKeyboardButton("❌ Close", callback_data="close_view")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _show_card_details_from_query(self, query, card: Dict[str, Any]):
        """Show card details from callback query."""
        message = (
            f"💳 **{card['bank_name']} Credit Card**\n\n"
            f"🏦 **Bank:** {card['bank_name']}\n"
            f"💳 **Card Number:** •••• {card['card_number']}\n"
            f"📅 **Expiry Date:** {card['expiry_date']}\n"
        )
        
        if card.get('cvv'):
            message += f"🔐 **CVV:** {card['cvv']}\n"
        
        if card.get('full_card_number'):
            message += f"🔢 **Full Number:** {card['full_card_number']}\n"
        
        message += f"\n📅 **Added:** {card['created_at']}"
        
        keyboard = [
            [InlineKeyboardButton("🗑️ Delete Card", callback_data=f"confirm_delete_{card['id']}")],
            [InlineKeyboardButton("❌ Close", callback_data="close_view")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _show_card_for_deletion(self, update: Update, card: Dict[str, Any]):
        """Show card for deletion confirmation."""
        message = (
            f"🗑️ **Delete Credit Card**\n\n"
            f"Are you sure you want to delete this card?\n\n"
            f"🏦 **Bank:** {card['bank_name']}\n"
            f"💳 **Card Number:** •••• {card['card_number']}\n"
            f"📅 **Expiry Date:** {card['expiry_date']}\n\n"
            "⚠️ This action cannot be undone!"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Yes, Delete", callback_data=f"confirm_delete_{card['id']}"),
                InlineKeyboardButton("❌ Cancel", callback_data="close_view")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _show_card_for_deletion_from_query(self, query, card: Dict[str, Any]):
        """Show card for deletion confirmation from callback query."""
        message = (
            f"🗑️ **Delete Credit Card**\n\n"
            f"Are you sure you want to delete this card?\n\n"
            f"🏦 **Bank:** {card['bank_name']}\n"
            f"💳 **Card Number:** •••• {card['card_number']}\n"
            f"📅 **Expiry Date:** {card['expiry_date']}\n\n"
            "⚠️ This action cannot be undone!"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Yes, Delete", callback_data=f"confirm_delete_{card['id']}"),
                InlineKeyboardButton("❌ Cancel", callback_data="close_view")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown') 