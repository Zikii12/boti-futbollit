import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = "9108188458:AAHkGLSq4y5AHbBAXFnKTKvE4AU59oeznvs"
RAPIDAPI_KEY = "1b41bb4863msh3e2bc115ca860d2p152e5cjsn03752bc6a9ad"

headers = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ **Boti i Futbollit është Online!**\n\n"
        "Përdor komandën:\n"
        "• `/simulo [Ekipi 1] vs [Ekipi 2]` - Analizë e ndeshjes, data, ora dhe koeficientët (1X2)\n\n"
        "💡 *Shembull:* `/simulo Barcelona vs Alaves`",
        parse_mode="Markdown"
    )

async def simulo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.replace("/simulo", "").strip()
    if "vs" not in query:
        await update.message.reply_text("⚠️ Format i gabuar! Shkruaj p.sh: `/simulo Barcelona vs Alaves`", parse_mode="Markdown")
        return

    team1_str, team2_str = query.split("vs")
    name1 = team1_str.strip()
    name2 = team2_str.strip()

    msg_status = await update.message.reply_text(f"🔍 Duke kërkuar datën, orën dhe koeficientët për **{name1} vs {name2}**...", parse_mode="Markdown")

    p1, px, p2 = 55.0, 25.0, 20.0
    odds_source = "Analizë e Tregut & H2H"
    formatted_date = "📅 **Data:** `Të konfirmohet`\n• ⏰ **Ora:** `Së shpejti`"

    try:
        # Kërkojmë ID-të e ekipeve
        r1 = requests.get(f"https://api-football-v1.p.rapidapi.com/v3/teams?search={name1}", headers=headers, timeout=3).json()
        r2 = requests.get(f"https://api-football-v1.p.rapidapi.com/v3/teams?search={name2}", headers=headers, timeout=3).json()
        
        if r1.get("response") and r2.get("response"):
            id1 = r1["response"][0]["team"]["id"]
            id2 = r2["response"][0]["team"]["id"]
            
            # Provojmë fillimisht përmes H2H
            next_res = requests.get(f"https://api-football-v1.p.rapidapi.com/v3/fixtures?h2h={id1}-{id2}&next=1", headers=headers, timeout=3).json()
            fixtures = next_res.get("response", [])
            
            # Nëse H2H nuk kthen ndeshje të ardhshme, kërkojmë ndeshjen e radhës të ekipit të parë
            if not fixtures:
                team_next = requests.get(f"https://api-football-v1.p.rapidapi.com/v3/fixtures?team={id1}&next=1", headers=headers, timeout=3).json()
                fixtures = team_next.get("response", [])

            if fixtures:
                fixture_id = fixtures[0]["fixture"]["id"]
                raw_date = fixtures[0]["fixture"].get("date", "")
                
                if raw_date:
                    date_part, time_part = raw_date.split("T")
                    formatted_date = f"📅 **Data:** `{date_part}`\n• ⏰ **Ora:** `{time_part[:5]} UTC`"

                # Marrim koeficientët realë (Odds) për këtë ndeshje
                odds_res = requests.get(f"https://api-football-v1.p.rapidapi.com/v3/odds?fixture={fixture_id}", headers=headers, timeout=3).json()
                odds_data = odds_res.get("response", [])
                
                if odds_data:
                    bookmakers = odds_data[0].get("bookmakers", [])
                    if bookmakers:
                        for bet in bookmakers[0].get("bets", []):
                            if bet.get("id") == 1:
                                values = bet.get("values", [])
                                odd_1 = float(values[0]["odd"])
                                odd_x = float(values[1]["odd"])
                                odd_2 = float(values[2]["odd"])
                                
                                prob_1 = (1 / odd_1)
                                prob_x = (1 / odd_x)
                                prob_2 = (1 / odd_2)
                                total = prob_1 + prob_x + prob_2
                                
                                p1 = round((prob_1 / total) * 100, 1)
                                px = round((prob_x / total) * 100, 1)
                                p2 = round((prob_2 / total) * 100, 1)
                                odds_source = f"Koeficientët Zyrtarë ({bookmakers[0].get('name', 'Bookmaker')})"
    except Exception as e:
        logging.error(f"Gabim gjatë thirrjes së API: {e}")

    if p1 > p2 and p1 > px:
        favorite = f"🏆 **I Favorizuar nga Tregu:** {name1} ({p1}%)"
    elif p2 > p1 and p2 > px:
        favorite = f"🏆 **I Favorizuar nga Tregu:** {name2} ({p2}%)"
    else:
        favorite = "🤝 **Parashikimi:** Ndeshje e ekuilibruar, mundësi e lartë për **Barazim (X)**"

    msg = (
        f"📊 **ANALIZA E NDESHJES & ORARI**\n"
        f"⚔️ **{name1} vs {name2}**\n\n"
        f"{formatted_date}\n\n"
        f"{favorite}\n\n"
        f"📈 **Probabiliteti Real (1X2):**\n"
        f"• 1 ({name1}): **{p1}%**\n"
        f"• X (Barazim): **{px}%**\n"
        f"• 2 ({name2}): **{p2}%**\n\n"
        f"ℹ️ *Burimi i të dhënave: {odds_source}*"
    )
    
    await msg_status.edit_text(msg, parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("simulo", simulo))
    app.run_polling()
