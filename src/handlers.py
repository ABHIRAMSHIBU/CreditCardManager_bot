import logging
from typing import Dict, Any, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .database import DatabaseManager
from .form_manager import FormManager, FormState

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
            "/help - Show this help message\n\n"
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
            "• `/help` - Show this help message\n\n"
            "**Examples:**\n"
            "• `/view_card HDFC` - View HDFC card\n"
            "• `/view_card 1234` - View card ending with 1234\n"
            "• `/delete_card 5678` - Delete card ending with 5678\n\n"
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