from dotenv import dotenv_values
import logging
from telegram import Update, constants
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from change_filter import create_user_filters, load_filters
from helpers import stringify_filters

config = dotenv_values(".env")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="bot.log"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    create_user_filters(update.effective_user.id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to Youtube channel bot!")

async def show_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filters = load_filters(update.effective_user.id)
    message = stringify_filters(filters)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=constants.ParseMode.MARKDOWN_V2)


if __name__ == "__main__":
    application = ApplicationBuilder().token(config["BOT_API_TOKEN"]).build()
    
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    
    show_filters_handler = CommandHandler("show_filters", show_filters)
    application.add_handler(show_filters_handler)
    
    application.run_polling()