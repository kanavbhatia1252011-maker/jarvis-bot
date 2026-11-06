import os
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import google.generativeai as genai

TELEGRAM_TOKEN = "9152846224:AAHGRMDWj-T7106b5_YwBHAhYIycyY0a-Y"
GEMINI_KEY = "AQ.Ab8RN6JyOIYAK1ldpFR661Z9-p0pTaHxnlWHOsoEL0I99wPYWQ"
RENDER_URL = "https://jarvis-bot-2vnm.onrender.com"
CALLMEBOT_USERNAME = "KanavBhatia"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Telegram send error:", e)

def ring_phone(reason):
    url = f"https://api.callmebot.com/start.php?user=@{CALLMEBOT_USERNAME}&text={reason}&lang=en-US-Standard-B&rpt=2"
    try:
        requests.get(url, timeout=10)
    except Exception as e:
        print("CallMeBot error:", e)

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"JARVIS Server Live 24/7!")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

        try:
            data = json.loads(post_data.decode('utf-8'))
            if "message" in data and "text" in data["message"]:
                chat_id = data["message"]["chat"]["id"]
                user_msg = data["message"]["text"]

                if "call me" in user_msg.lower() or "emergency" in user_msg.lower():
                    send_telegram_message(chat_id, "📞 Triggering CallMeBot phone call now...")
                    ring_phone("Emergency alert requested from JARVIS.")
                    return

                response = model.generate_content(f"You are JARVIS, a personal AI assistant. Be direct and concise. User: {user_msg}")
                send_telegram_message(chat_id, response.text)
        except Exception as e:
            print("Processing Error:", e)

def run():
    webhook_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={RENDER_URL}"
    try:
        requests.get(webhook_url, timeout=10)
        print("Webhook registered successfully!")
    except Exception as e:
        print("Failed to register webhook:", e)

    port = int(os.environ.get("PORT", 10000))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"JARVIS running on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
    
