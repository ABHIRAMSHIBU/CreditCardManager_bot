# Credit Card Managment Bot

## Functionality

### Basic Functionality

- Add a new credit card
- View all credit cards
- View a specific credit card
- Delete a credit card
- Set billing date
- Set bill amount
- Remind user to pay the bill

### Advanced Functionality

- Create a new wallet for the card.
- Get card number + expiry + cvv (stored in a password protected database).
- Get card bill using pdf.
- Process Encrypted PDF.
- Get card bill from message.
- AI Integration.

## Functionality Exp

### Basic Functionality

1. Add a new credit card.
    - User can use add command to add a new credit card.
         - Need to ask Bank Name, Last 4 digits of card number, Expiry Date.
         - No need to encrypt as long as its 4 digits and no CVV is present.
         - User can opt out of full card number and CVV

    Example:
    User: /add-card
    Bot: Creates a form to fill the details with buttons to select which field to fill.
         Buttons Bank Name, Card Number, Expiry Date, CVV, Done.
    User: User clicks on Bank Name button.
    Bot: Alright tell me the bank name.
    User: User says "HDFC"
    Bot: Shows the buttons again.
    User: Click on Card Number button.
    Bot: Alright tell me the last 4 digits of the card number or full card number.
    User: User says "1234"
    Bot: Shows the buttons again.
    User: Click on Expiry Date button.
    Bot: Alright tell me the expiry date.
    User: User says "01/2025"
    Bot: Shows the buttons again.
    User: Click on CVV button.
    Bot: Alright tell me the CVV.
    User: User says "123"
    Bot: Shows the buttons again.
    User: Click on Done button.
    Bot: Saves the details and shows a success message.
         - Bot checks if the card number is full, if yes there is a need for CVV and encrypted wallet.
         - Otherwise bot just requires last 4 digits of card number, Expiry Date, Bank Name, CVV is not required.
    Example:
    User: /add-card
    Bot: Creates a form to fill the details with buttons to select which field to fill.
2. View all credit cards.
    - User can use view command to view all credit cards.
         - Need to show all credit cards in a list.
         - User can select a credit card to view more details.
    Example: 
    User: /view-cards
    Bot: Shows buttons for card with 4 char of bank name and last 4 digits of card number.
    User: User clicks on a card.
    Bot: Shows all details of the card.
    Bot: Shows back button.
    User: User clicks on back button.
    Bot: Shows the buttons again.
    User: User clicks on a card.
    Bot: Shows all details of the card.
    Bot: Shows back button.
    User: User clicks on back button.
    Bot: Shows the buttons again.
    User: Clicks on done button.

3. View a specific credit card.
    - User can use view command to view a specific credit card.
         - Need to show all details of the credit card.
         - User can use back command to go back to the list of credit cards.
    Example:
    User: /view-card 1234 or HDFC
    Bot: Shows all details of the card.

    In case of ambiguity, bot can ask user to select the card from the list of cards.
    Example:
    User: /view-card HDFC
    Bot: Shows buttons for card with 4 char of bank name and last 4 digits of card number.
    User: User clicks on a card.
    Bot: Shows all details of the card.
    Bot: Shows back button.

4. Delete a credit card.
    - User can delete a card given the last 4 digits of card number or bank name.
    Example:
    User: /delete-card 1234 or HDFC
    Bot: Shows all details of the card.
    Bot: Shows delete button.
    User: User clicks on delete button.
    Bot: Shows a success message.
    Bot: Shows the buttons again.

    In case of ambiguity, bot can ask user to select the card from the list of cards.
    Example:
    User: /delete-card HDFC
    Bot: Shows buttons for card with 4 char of bank name and last 4 digits of card number.
    User: User clicks on a card.
    Bot: Shows all details of the card.
    Bot: Shows delete button.
    User: User clicks on delete button.
    Bot: Shows a success message.
    Bot: Shows the buttons again.

