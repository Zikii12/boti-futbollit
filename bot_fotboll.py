import time
import requests

TOKEN = "9108188458:AAG6HdFqI1NKpYshRPNQR-C6ej4iX4zJbAc"
URL = f"https://api.telegram.org/bot{TOKEN}/"

print("Boti i futbollit u ndez!")

def main():
    last_id = None
    while True:
        try:
            res = requests.get(URL + "getUpdates", params={"offset": last_id, "timeout": 30}).json()
            for update in res.get("result", []):
                last_id = update["update_id"] + 1
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"]["text"]
                    
                    if text == "/start":
                        mesazhi = (
                            "⚽ **Boti i Futbollit është Online!**\n\n"
                            "Përdor komandën:\n"
                            "• /ndeshjet - Për të parë ndeshjet e sotme\n"
                            "• /simulo [Ekipi 1] vs [Ekipi 2] - Analizë e ndeshjes"
                        )
                        requests.get(URL + "sendMessage", params={
                            "chat_id": chat_id, 
                            "text": mesazhi,
                            "parse_mode": "Markdown"
                        })
                    
                    elif text == "/ndeshjet":
                        mesazhi = (
                            "⚽ **Ndeshjet dhe Parashikimet për Sot:**\n\n"
                            "🏆 *Premier League*\n"
                            "• Arsenal vs Chelsea ➡️ **1 & 2+** (Risk i Ulët)\n"
                            "• Man City vs Liverpool ➡️ **GG & Over 2.5**\n\n"
                            "🏆 *Serie A*\n"
                            "• Inter vs Milan ➡️ **1X & Under 3.5**"
                        )
                        requests.get(URL + "sendMessage", params={
                            "chat_id": chat_id, 
                            "text": mesazhi,
                            "parse_mode": "Markdown"
                        })
                    
                    else:
                        requests.get(URL + "sendMessage", params={
                            "chat_id": chat_id, 
                            "text": "Për të parë ndeshjet dhe parashikimet e sotme, dërgo komandën: /ndeshjet"
                        })
        except Exception as e:
            print("Gabim:", e)
        time.sleep(2)

if __name__ == '__main__':
    main()
