import re
import logging
import os

from dotenv import load_dotenv
from telegram import Update, constants, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler

from change_filter import create_user_filters, load_filters, change_filter_property
from youtube_api import get_channels
from helpers import stringify_filters, make_readable
from table_generators import get_table_image, get_pretty_table

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="bot.log"
)

async def display_channels(update, context, channels, message_to_edit=None):
    if not channels:
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message_to_edit.id, text="No channels were found")
        return
    image = get_table_image(channels)
    if image:
        if message_to_edit is not None:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_to_edit.id)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image)
    else:
        table = get_pretty_table(channels)
        if message_to_edit is not None:
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message_to_edit.id, text=table, parse_mode=constants.ParseMode.HTML)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=table, parse_mode=constants.ParseMode.HTML)

async def add_search_options_buttons(context, update):
    channels = context.user_data["last_query_results"]
    results_page = context.user_data["results_page"]

    buttons = []
    if len(channels) > results_page * 5:
        buttons.append([InlineKeyboardButton("Next page", callback_data="next_page")])

    buttons.append([InlineKeyboardButton("Get channel's url", callback_data="get_channel_url")])
    buttons.append([InlineKeyboardButton("Back", callback_data="back")])
    
    menu = InlineKeyboardMarkup(buttons)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Actions:", reply_markup=menu)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    create_user_filters(update.effective_user.id)
    context.user_data["context_mode"] = "general"
    await context.bot.set_my_commands([
        BotCommand("show_filters", "Show current filters"),
        BotCommand("edit_filters", "Edit filters"),
        BotCommand("search", "Search channels")
    ])
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
    elif query.data == "next_page":
        channels = context.user_data["last_query_results"]
        results_page = context.user_data["results_page"] + 1
        context.user_data["results_page"] = results_page

        await display_channels(update, context, channels[(results_page-1)*5:results_page*5])
        await add_search_options_buttons(context, update)
    elif query.data == "get_channel_url":
        await query.edit_message_text(text="Enter channel #")
    elif query.data == "back":
        context.user_data.clear()
        context.user_data["context_mode"] = "general"
        await context.bot.send_message(chat_id=query.message.chat.id, text="You are in the main menu")

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
        channels = get_channels(query, 50, update.effective_user.id, keys=["title", "subscribers_count", "total_views", "channel_url"])
        
        await display_channels(update, context, channels[:5], msg)
        
        if channels:
            context.user_data["context_mode"] = "search_results"
            context.user_data["last_query_results"] = channels
            context.user_data["results_page"] = 1
            await add_search_options_buttons(context, update)
    elif context.user_data["context_mode"] == "search_results":
        i = int(update.message["text"]) - 1
        if i < 0 or i >= len(context.user_data["last_query_results"]):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Number you specified is not correct")
        else:
            channel_url = context.user_data["last_query_results"][i]["channel_url"]
            await context.bot.send_message(chat_id=update.effective_chat.id, text=channel_url)
            await add_search_options_buttons(context, update)




if __name__ == "__main__":
    application = ApplicationBuilder().token(os.environ.get("BOT_API_TOKEN")).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("show_filters", show_filters))
    application.add_handler(CommandHandler("edit_filters", edit_filters))
    application.add_handler(CommandHandler("search", search))

    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters=None, callback=handle_messages))
    
    application.run_polling()