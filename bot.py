from dotenv import dotenv_values
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from change_filter import create_user_filters

config = dotenv_values(".env")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="bot.log"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    create_user_filters(update.effective_user.id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! ")

if __name__ == "__main__":
    application = ApplicationBuilder().token(config["BOT_API_TOKEN"]).build()
    
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    
    application.run_polling()