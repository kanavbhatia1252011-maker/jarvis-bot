import os
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import google.generativeai as genai

# --- CREDENTIALS ---
GEMINI_KEY = "AQ.Ab8RN6JyOIYAK1ldpFR661Z9-p0pTaHxnlWHOsoEL0I99wPYWQ"
TELEGRAM_TOKEN = "9152846224:AAHGRMDWj-T7106b5_YwBHAhYIycyY0a-Y"
CALLMEBOT_USERNAME = "KanavBhatia" # Make sure this is your exact Telegram username

# --- INITIALIZE AI & BOT ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# --- FUNCTIONS ---
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
        await context.bot.send_message(chat_id=chat_id, text="📞 Calling your phone right now...")
        ring_phone("Emergency alert triggered by JARVIS assistant.")
        return

    # Standard AI Reply
    try:
        prompt = f"You are JARVIS, a personal AI assistant. Be direct, helpful, and concise. User message: {user_msg}"
        response = model.generate_content(prompt)
        await context.bot.send_message(chat_id=chat_id, text=response.text)
    except Exception as e:
        print("Gemini error:", e)
        await context.bot.send_message(chat_id=chat_id, text="Sorry, I ran into an error.")

# Add handler to the bot application
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler))

# --- FLASK SERVER (For Render & Webhooks) ---
app = Flask(__name__)

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
async def webhook():
    # This receives the message from Telegram
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "OK", 200

@app.route("/")
def home():
    return "JARVIS is running!"

# --- STARTUP SEQUENCE ---
if __name__ == "__main__":
    # 1. Tell Telegram to send messages to your Render URL
    RENDER_URL = "https://jarvis-bot-2vnm.onrender.com" # YOUR URL FROM THE SCREENSHOT
    webhook_url = f"{RENDER_URL}/{TELEGRAM_TOKEN}"
    
    # We set the webhook before starting the Flask app
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}")
    print(f"Webhook set to: {webhook_url}")

    # 2. Start Flask on the Render port
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
