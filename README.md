# Credit Card Management Bot

A secure Telegram bot for managing credit card information with complete user data isolation. Each user can only access their own data, ensuring privacy and security.

## Features

### Basic Functionality
- ✅ Add new credit cards with interactive forms
- ✅ View all your credit cards
- ✅ View specific cards by bank name or last 4 digits
- ✅ Delete credit cards
- ✅ User data isolation (each user only sees their own data)
- ✅ Secure data storage with SQLite

### Advanced Features (Planned)
- 🔒 Encrypted wallet support
- 📄 PDF bill processing
- 🤖 AI integration with Ollama
- 💳 Full card number and CVV storage (encrypted)

## Technology Stack

- **Frontend**: Telegram Bot API
- **Backend**: Python 3.8+
- **Database**: SQLite3
- **Encryption**: pycryptodome (for future phases)
- **AI Integration**: Ollama (for future phases)

## Installation

### Prerequisites
- Python 3.8 or higher
- A Telegram Bot Token (get from [@BotFather](https://t.me/botfather))

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CreditCardManager_bot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your Telegram bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   DATABASE_PATH=credit_cards.db
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

## Usage

### Commands

- `/start` - Welcome message and bot introduction
- `/help` - Show all available commands
- `/add_card` - Add a new credit card with interactive form
- `/view_cards` - View all your credit cards
- `/view_card <search>` - View a specific card by bank name or last 4 digits
- `/delete_card <search>` - Delete a card by bank name or last 4 digits

### Examples

```
/add_card
> Bot shows interactive form with buttons for each field

/view_cards
> Bot shows list of all your cards with selection buttons

/view_card HDFC
> Bot shows HDFC card details (or selection menu if multiple)

/view_card 1234
> Bot shows card ending with 1234

/delete_card 5678
> Bot shows confirmation for deleting card ending with 5678
```

## Security Features

- **User Isolation**: Each user can only access their own credit card data
- **Data Validation**: All input is validated before storage
- **Secure Storage**: Data is stored in SQLite with proper user separation
- **No Data Leakage**: Users cannot access other users' information

## Project Structure

```
CreditCardManager_bot/
├── src/
│   ├── __init__.py
│   ├── bot.py              # Main bot application
│   ├── config.py           # Configuration management
│   ├── database.py         # Database operations
│   ├── form_manager.py     # Form state management
│   └── handlers.py         # Command and message handlers
├── tests/
│   ├── __init__.py
│   ├── test_database.py    # Database tests
│   └── test_form_manager.py # Form manager tests
├── docs/
│   ├── functionality.md    # Detailed functionality specs
│   ├── implementation-plan.md # Development phases
│   └── technology-stack.md # Tech stack details
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── pytest.ini            # Test configuration
├── env.example           # Environment variables template
└── README.md             # This file
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_database.py

# Run with coverage
pytest --cov=src
```

## Development Phases

### Phase 1 (Current)
- ✅ Basic functionality implementation
- ✅ User data isolation
- ✅ Interactive forms
- ✅ Database operations

### Phase 2 (Future)
- 🔒 Encrypted wallet support
- 🔒 Advanced encryption features
- 📄 PDF bill processing

### Phase 3 (Future)
- 🤖 AI integration with Ollama
- 🧠 Smart bill analysis
- 📊 Spending insights

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:

1. Check the [documentation](docs/)
2. Run the test suite to verify your setup
3. Create an issue with detailed information about your problem

## Security Notice

This bot stores sensitive credit card information. While it implements user isolation and data validation, it's recommended to:

- Use strong, unique passwords for your Telegram account
- Regularly review and delete unnecessary card information
- Be cautious when sharing your bot token
- Consider the security implications before storing full card numbers and CVVs 