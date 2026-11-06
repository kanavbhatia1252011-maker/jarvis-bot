import os
import requests
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from google import genai

TELEGRAM_TOKEN = "9152846224:AAHGRMDWj-T7106b5_YwBHAhYIycyY0a-Y"
GEMINI_KEY = "AQ.Ab8RN6JyOIYAK1ldpFR661Z9-p0pTaHxnlWHOsoEL0I99wPYWQ"
RENDER_URL = "https://jarvis-bot-2vnm.onrender.com"
CALLMEBOT_USERNAME = "KanavBhatia"

# Initialize Gemini async client
genai_client = genai.Client(api_key=GEMINI_KEY)

# Initialize Telegram App
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
        response = await genai_client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"You are JARVIS, a personal AI assistant. Be direct, helpful, and concise. User: {user_msg}"
        )
        await context.bot.send_message(chat_id=chat_id, text=response.text)
    except Exception as e:
        print("Gemini API Error:", e)
        await context.bot.send_message(chat_id=chat_id, text="Sorry, I ran into an error processing that.")

telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Set webhook on startup
    webhook_url = f"{RENDER_URL}/{TELEGRAM_TOKEN}"
    await telegram_app.bot.set_webhook(url=webhook_url)
    async with telegram_app:
        await telegram_app.start()
        print("JARVIS Webhook set & ready!")
        yield
        await telegram_app.stop()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def home():
    return {"status": "JARVIS is online 24/7!"}

@app.post(f"/{TELEGRAM_TOKEN}")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
