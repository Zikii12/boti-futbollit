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
                    
                    if text == "/start" or text == "/ndeshjet":
                        mesazhi = (
                            "⚽ **Përshëndetje! Këtu janë parashikimet për ndeshjet e sotme:**\n\n"
                            "🏆 *Premier League / Serie A / etj.*\n"
                            "• Ndeshja 1: 1 & Gola (Parashikim i sugjeruar)\n"
                            "• Ndeshja 2: X2 & 2+ (Formë e mirë e miqve)\n\n"
                            "Për më shumë analiza, shkruaj opsionet e tjera!"
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
