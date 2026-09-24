import os
import logging
from flask import Flask
from threading import Thread

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

INSTAGRAM_URL = "https://www.instagram.com/spiderp4nel?stkn=MWZ2bGh1anlwZWZ6Yw=="
TELEGRAM_URL = "https://t.me/zyronpanelshop"

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Instagram Follow", url=INSTAGRAM_URL)],
        [InlineKeyboardButton("📢 Telegram Join", url=TELEGRAM_URL)],
        [InlineKeyboardButton("✅ Done", callback_data="done")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "1️⃣ Instagram Follow karo\n"
        "2️⃣ Telegram Join karo\n"
        "3️⃣ Done button dabao\n"
        "4️⃣ Screenshot bhejo\n\n"
        "Admin screenshot verify karega.",
        reply_markup=menu()
    )

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Your Telegram ID:\n{update.effective_user.id}"
    )

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "📸 Ab Instagram aur Telegram ka screenshot bhejo."
    )

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    picture = update.message.photo[-1]

    caption = (
        "📥 NEW VERIFICATION\n\n"
        f"👤 Name: {user.full_name}\n"
        f"🆔 ID: {user.id}\n"
        f"👤 Username: @{user.username or 'N/A'}"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Approve",
                callback_data=f"approve_{user.id}"
            ),
            InlineKeyboardButton(
                "❌ Reject",
                callback_data=f"reject_{user.id}"
            )
        ]
    ])

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=picture.file_id,
        caption=caption,
        reply_markup=buttons
    )

    await update.message.reply_text(
        "✅ Screenshot mil gaya.\n"
        "Admin verification ke baad result milega."
    )

async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer("Not authorized.", show_alert=True)
        return

    await query.answer()

    if query.data.startswith("approve_"):
        user_id = int(query.data.split("_")[1])

        await context.bot.send_message(
            chat_id=user_id,
            text="🎉 Verification Approved!\n\n🗳️ Ab aap Vote kar sakte ho."
        )

        await query.edit_message_caption(
            caption=query.message.caption + "\n\n✅ APPROVED"
        )

    elif query.data.startswith("reject_"):
        user_id = int(query.data.split("_")[1])

        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Verification rejected.\n\n"
                 "Please correct screenshot and send again."
        )

        await query.edit_message_caption(
            caption=query.message.caption + "\n\n❌ REJECTED"
        )

def web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def main():
    bot = Application.builder().token(BOT_TOKEN).build()

    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CommandHandler("id", myid))

    bot.add_handler(
        CallbackQueryHandler(done, pattern="^done$")
    )

    bot.add_handler(
        CallbackQueryHandler(
            admin_action,
            pattern=r"^(approve_|reject_)"
        )
    )

    bot.add_handler(
        MessageHandler(filters.PHOTO, photo)
    )

    Thread(target=web_server, daemon=True).start()

    bot.run_polling()

if __name__ == "__main__":
    main()
