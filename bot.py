import logging
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import os 
from dotenv import load_dotenv
load_dotenv()
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URI")# Replace with your backend URL

# Define the /start command handler
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Use /create_wallet to create a new Solana wallet.')

# Define the /create_wallet command handler
def create_wallet(update: Update, context: CallbackContext) -> None:
    response = requests.post(f"{BACKEND_URL}/create_wallet")
    if response.status_code == 200:
        data = response.json()
        public_key = data['public_key']
        private_key = data.get('private_key')
        qr_code = data['qr_code']
        balance = data['balance']

        message = f"Wallet created!\n\nPublic Key: {public_key}\nBalance: {balance} Lamports"
        update.message.reply_text(message)
        
        # Send QR code image
        update.message.reply_photo(photo=f"data:image/png;base64,{qr_code}")

        # Send private key as a private message
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Private Key: {private_key}", parse_mode='Markdown')
    else:
        update.message.reply_text('Failed to create wallet. Please try again.')

# Define the main function
def main() -> None:
    # Bot token
    TOKEN = os.getenv("BOT_TOKEN")  # Replace with your bot token

    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("create_wallet", create_wallet))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM, or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
