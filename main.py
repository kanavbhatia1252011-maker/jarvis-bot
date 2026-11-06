import os
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from google import genai

TELEGRAM_TOKEN = "9152846224:AAHGRMDWj-T7106b5_YwBHAhYIycyY0a-Y"
GEMINI_KEY = "AQ.Ab8RN6JyOIYAK1ldpFR661Z9-p0pTaHxnlWHOsoEL0I99wPYWQ"
RENDER_URL = "https://jarvis-bot-2vnm.onrender.com"
CALLMEBOT_USERNAME = "KanavBhatia"

client = genai.Client(api_key=GEMINI_KEY)
flask_app = Flask(__name__)

# Setup Telegram Application without running an internal loop
telegram_app = Application.builder().token(TELEGRAM_TOKEN).updater(None).build()

def ring_phone(reason: str):
    url = f"https://api.callmebot.com/start.php?user=@{CALLMEBOT_USERNAME}&text={reason}&lang=en-US-Standard-B&rpt=2"
    try:
        requests.get(url, timeout=10)
    except Exception as e:
        print("CallMeBot error:", e)

async def reply_handler(update: Update, context):
    if not update.message or not update.message.text:
        return
        
    user_msg = update.message.text
    chat_id = update.effective_chat.id

    if "call me" in user_msg.lower() or "emergency" in user_msg.lower():
        await context.bot.send_message(chat_id=chat_id, text="📞 Calling your phone right now...")
        ring_phone("Emergency alert triggered by JARVIS assistant.")
        return

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"You are JARVIS, a personal AI assistant. Be direct, helpful, and concise. User: {user_msg}"
        )
        await context.bot.send_message(chat_id=chat_id, text=response.text)
    except Exception as e:
        print("Gemini API Error:", e)
        await context.bot.send_message(chat_id=chat_id, text="Sorry, I ran into an error processing that.")

telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler))

@flask_app.route('/')
def home():
    return "JARVIS Webhook Server is Live!"

@flask_app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    import asyncio
    json_data = request.get_json(force=True)
    update = Update.de_json(json_data, telegram_app.bot)
    
    async def process():
        await telegram_app.initialize()
        await telegram_app.process_update(update)
        
    asyncio.run(process())
    return "OK", 200

if __name__ == "__main__":
    # Automatically register the webhook URL with Telegram
    set_webhook_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={RENDER_URL}/{TELEGRAM_TOKEN}"
    try:
        requests.get(set_webhook_url, timeout=10)
    except Exception as e:
        print("Webhook registration error:", e)

    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
