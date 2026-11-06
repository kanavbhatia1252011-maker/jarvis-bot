import os
import asyncio
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import google.generativeai as genai

# Credentials
GEMINI_KEY = "AQ.Ab8RN6JyOIYAK1ldpFR661Z9-p0pTaHxnlWHOsoEL0I99wPYWQ"
TELEGRAM_TOKEN = "9152846224:AAHGRMDWj-T7106b5_YwBHAhYIycyY0a-Y"
CALLMEBOT_USERNAME = "KanavBhatia"

# Initialize Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Flask Web Server (keeps Render health check alive on PORT 10000)
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "JARVIS is online and running 24/7!"

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

    # Emergency Trigger
    if "call me" in user_msg.lower() or "emergency" in user_msg.lower():
        await context.bot.send_message(chat_id=chat_id, text="📞 Triggering phone call right now...")
        ring_phone("Emergency alert triggered by JARVIS assistant.")
        return

    # AI Reply
    try:
        prompt = f"You are JARVIS, a personal AI assistant. Be direct, helpful, and concise. User: {user_msg}"
        response = model.generate_content(prompt)
        await context.bot.send_message(chat_id=chat_id, text=response.text)
    except Exception as e:
        print("Gemini error:", e)
        await context.bot.send_message(chat_id=chat_id, text="Sorry, I ran into an error generating a response.")

def run_telegram_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler))
    print("JARVIS Telegram Bot started...")
    app.run_polling()

if __name__ == "__main__":
    # Start Telegram Bot in background thread
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    
    # Run Flask on main thread so Render binds to PORT 10000 cleanly
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
