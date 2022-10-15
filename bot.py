import re
import logging

from dotenv import dotenv_values
from telegram import Update, constants, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler

from change_filter import create_user_filters, load_filters, change_filter_property
from youtube_api import get_channels
from helpers import stringify_filters, make_readable, prettify_number, trim_string
from table_generators import get_table_image, get_pretty_table

config = dotenv_values(".env")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="bot.log"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    create_user_filters(update.effective_user.id)
    context.user_data["context_mode"] = "general"
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to Youtube channel bot!")

async def show_filters(update, context):
    filters = load_filters(update.effective_user.id)
    message = stringify_filters(filters)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=constants.ParseMode.MARKDOWN_V2)

async def edit_filters(update, context):
    filters = load_filters(update.effective_user.id)
    buttons = []
    for key in filters.keys():
        buttons.append([InlineKeyboardButton(make_readable(key), callback_data=f"edit_filter {key}")])
    menu = InlineKeyboardMarkup(buttons)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Choose filter to edit:", reply_markup=menu)

async def search(update, context):
    context.user_data["context_mode"] = "search"
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter a search query:")

async def handle_callback_query(update, context):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("edit_filter"):
        filter_key = query.data.split(" ")[1]
        await query.edit_message_text(text=f'Editing "{make_readable(filter_key)}"')

        context.user_data["context_mode"] = "edit_filter"
        context.user_data["filter_key"] = filter_key
        context.user_data["lower_limit"] = None
        context.user_data["upper_limit"] = None

        await context.bot.send_message(chat_id=query.message.chat.id, text="Enter lower limit:")

async def handle_messages(update, context):
    if context.user_data["context_mode"] == "edit_filter":
        val = update.message["text"]
        if re.match(r"-?\d+", val) and int(val) >= -1:
            if context.user_data["lower_limit"] is None:
                lower_limit = 0 if int(val) == -1 else int(val)
                context.user_data["lower_limit"] = lower_limit
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter upper limit (-1 for no limit):")
            else:
                upper_limit = "no_upper_limit" if int(val) == -1 else int(val)
                if isinstance(upper_limit, int) and upper_limit < context.user_data["lower_limit"]:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text="Upper limit shouldn't be less than lower limit")
                else:
                    change_filter_property(update.effective_user.id, context.user_data["filter_key"], context.user_data["lower_limit"], upper_limit)

                    context.user_data.clear()
                    context.user_data["context_mode"] = "general"
                    await context.bot.send_message(chat_id=update.effective_chat.id, text="Changes were saved")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to enter a non-negative integer")
    elif context.user_data["context_mode"] == "search":
        msg = await context.bot.send_message(chat_id=update.effective_chat.id, text="Wait a second...", parse_mode=constants.ParseMode.HTML)

        query = update.message["text"]
        channels = get_channels(query, 5, update.effective_user.id, keys=["title", "subscribers_count", "total_views"])
        image = get_table_image(channels)

        context.user_data["context_mode"] == "general"
        if image:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg.id)
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image)
        else:
            table = get_pretty_table(channels)
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.id, text=table, parse_mode=constants.ParseMode.HTML)


if __name__ == "__main__":
    application = ApplicationBuilder().token(config["BOT_API_TOKEN"]).build()
    
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    
    show_filters_handler = CommandHandler("show_filters", show_filters)
    application.add_handler(show_filters_handler)

    edit_filters_handler = CommandHandler("edit_filters", edit_filters)
    application.add_handler(edit_filters_handler)

    search_handler = CommandHandler("search", search)
    application.add_handler(search_handler)

    edit_filter_handler = CallbackQueryHandler(handle_callback_query)
    application.add_handler(edit_filter_handler)

    message_handler = MessageHandler(filters=None, callback=handle_messages)
    application.add_handler(message_handler)
    
    application.run_polling()