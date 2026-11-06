import os
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

# Credentials
GEMINI_KEY = "AQ.Ab8RN6JyOIYAK1ldpFR661Z9-p0pTaHxnlWHOsoEL0I99wPYWQ"
TELEGRAM_TOKEN = "9152846224:AAHGRMDWj-T7106b5_YwBHAhYIycyY0a-Y"
CALLMEBOT_USERNAME = "KanavBhatia"

# Flask keep-alive server for Render
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "JARVIS is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

# Initialize Gemini Client
client = genai.Client(api_key=GEMINI_KEY)

def ring_phone(alert_reason):
    url = f"https://api.callmebot.com/start.php?user=@{CALLMEBOT_USERNAME}&text={alert_reason}&lang=en-US-Standard-B&rpt=2"
    try:
        requests.get(url, timeout=10)
    except Exception as e:
        print("CallMeBot error:", e)

async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_msg = update.message.text
    chat_id = update.effective_chat.id

    # Emergency Call Trigger
    if "call me" in user_msg.lower() or "emergency" in user_msg.lower():
        await context.bot.send_message(chat_id=chat_id, text="📞 Calling your phone right now...")
        ring_phone("Emergency alert triggered by JARVIS assistant.")
        return

    # Standard AI Response
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"You are JARVIS, a personal AI assistant. Be direct, helpful, and concise. User message: {user_msg}"
        )
        await context.bot.send_message(chat_id=chat_id, text=response.text)
    except Exception as e:
        print("Gemini API error:", e)
        await context.bot.send_message(chat_id=chat_id, text="Sorry, I ran into an issue processing that request.")

if __name__ == "__main__":
    # Start Flask in background thread for Render health checks
    threading.Thread(target=run_flask, daemon=True).start()

    # Start Telegram Bot polling
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler))
    print("JARVIS is online...")
    app.run_polling()
