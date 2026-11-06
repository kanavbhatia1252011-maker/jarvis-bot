import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Your Token
TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN"

app = Flask(__name__)
# Initialize Application, but don't use polling
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Your handler function (keep as is)
async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... your logic ...
    pass

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler))

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    # Receive Telegram's update
    update = Update.de_json(request.get_json(force=True), application.bot)
    # Let the application process this update
    application.update_queue.put_nowait(update)
    return "OK", 200

if __name__ == "__main__":
    # On startup, tell Telegram where to send messages
    # Note: Render will automatically provide HTTPS, just fill in your onrender.com address
    WEBHOOK_URL = "https://jarvis-bot-2vnm.onrender.com/" + TELEGRAM_TOKEN
    application.bot.set_webhook(url=WEBHOOK_URL)
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
