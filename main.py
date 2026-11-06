import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import google.generativeai as genai

# Your Credentials
GEMINI_KEY = "AQ.Ab8RN6JyOIYAK1ldpFR661Z9-p0pTaHxnlWHOsoEL0I99wPYWQ"
TELEGRAM_TOKEN = "9152846224:AAHGRMDWj-T7106b5_YwBHAhYIycyY0a-Y"
CALLMEBOT_USERNAME = "knavvv"  # Replace with your Telegram username (without @)

# Initialize Gemini AI
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def ring_phone(alert_reason):
    url = f"https://api.callmebot.com/start.php?user=@{CALLMEBOT_USERNAME}&text={alert_reason}&lang=en-US-Standard-B&rpt=2"
    requests.get(url)

async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    chat_id = update.effective_chat.id

    # Emergency Trigger
    if "call me" in user_msg.lower() or "emergency" in user_msg.lower():
        await context.bot.send_message(chat_id=chat_id, text="📞 Calling your phone right now...")
        ring_phone("Emergency alert triggered by JARVIS assistant.")
        return

    # Standard AI Reply
    prompt = f"You are JARVIS, a personal AI assistant. Be direct, helpful, and concise. User message: {user_msg}"
    response = model.generate_content(prompt)
    await context.bot.send_message(chat_id=chat_id, text=response.text)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler))
    print("JARVIS is online...")
    app.run_polling()