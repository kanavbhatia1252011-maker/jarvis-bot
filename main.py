import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import google.generativeai as genai

# --- CREDENTIALS ---
GEMINI_KEY = "AQ.Ab8RN6JyOIYAK1ldpFR661Z9-p0pTaHxnlWHOsoEL0I99wPYWQ"
TELEGRAM_TOKEN = "9152846224:AAHGRMDWj-T7106b5_YwBHAhYIycyY0a-Y"
CALLMEBOT_USERNAME = "KanavBhatia"

# --- INITIALIZE ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# 建立 Application
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

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

    if "call me" in user_msg.lower() or "emergency" in user_msg.lower():
        await context.bot.send_message(chat_id=chat_id, text="📞 Calling your phone right now...")
        ring_phone("Emergency alert triggered by JARVIS assistant.")
        return

    try:
        prompt = f"You are JARVIS, a personal AI assistant. Be direct, helpful, and concise. User message: {user_msg}"
        response = model.generate_content(prompt)
        await context.bot.send_message(chat_id=chat_id, text=response.text)
    except Exception as e:
        print("Gemini error:", e)
        await context.bot.send_message(chat_id=chat_id, text="Sorry, I ran into an error.")

# 註冊處理器
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler))

# --- 啟動順序 (重要！不用 Flask 了) ---
if __name__ == "__main__":
    # 1. 你的 Render 網址
    RENDER_URL = "https://jarvis-bot-2vnm.onrender.com"
    # 2. 告訴 Telegram 把訊息推到這個網址
    webhook_url = f"{RENDER_URL}/{TELEGRAM_TOKEN}"
    
    port = int(os.environ.get("PORT", 10000))
    
    # 3. 使用內建的 Webhook 伺服器啟動 (它會自己處理好異步問題)
    print(f"Starting webhook server on port {port}...")
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TELEGRAM_TOKEN,
        webhook_url=webhook_url
    )
    
