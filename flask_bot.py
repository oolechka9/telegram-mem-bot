import json
import random
import os
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = "7011844694:AAFahpy5AsrMk0uWRTc3Ezd9t8E67bS97pU"
GROUP_ID = -1002567376440
PASTES_FILE = "pastes.json"

def load_pastes():
    if not os.path.exists(PASTES_FILE):
        with open(PASTES_FILE, "w") as f:
            json.dump([], f)
    with open(PASTES_FILE, "r") as f:
        return json.load(f)

def save_pastes(pastes):
    with open(PASTES_FILE, "w") as f:
        json.dump(pastes, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Прислать МакМем", callback_data="get_paste")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Жми кнопку и получи МакМем!", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pastes = load_pastes()
    if not pastes:
        await query.edit_message_text("Пока нет паст.")
        return
    message_id = random.choice(pastes)
    await context.bot.copy_message(chat_id=query.message.chat.id, from_chat_id=GROUP_ID, message_id=message_id)

async def handle_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.chat.id == GROUP_ID:
        pastes = load_pastes()
        msg_id = update.channel_post.message_id
        if msg_id not in pastes:
            pastes.append(msg_id)
            save_pastes(pastes)

flask_app = Flask(__name__)
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))
application.add_handler(MessageHandler(filters.ALL, handle_new_post))

import threading, asyncio
def run():
    async def runner():
        await application.initialize()
        await application.start()
    asyncio.run(runner())

threading.Thread(target=run).start()

@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK"

@flask_app.route("/")
def index():
    return "Бот работает!"
