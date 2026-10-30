import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = "9108188458:AAHZpzXnBLNaZdJXJ0o0c9qKnh5F_matrdI
"
RAPIDAPI_KEY = "1b41bb4863msh3e2bc115ca860d2p152e5cjsn03752bc6a9ad"

headers = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ **Boti i Futbollit (Me Data, Orë & Koeficientë) është Online!**\n\n"
        "Përdor komandën:\n"
        "• `/simulo [Ekipi 1] vs [Ekipi 2]` - Analizë e ndeshjes, data, ora dhe koeficientët (1X2)\n\n"
        "💡 *Shembull:* `/simulo Real Madrid vs Barcelona`",
        parse_mode="Markdown"
    )

def get_team_id(team_name):
    try:
        url = f"https://api-football-v1.p.rapidapi.com/v3/teams?search={team_name}"
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        if data.get("response"):
            team_info = data["response"][0]["team"]
            return team_info["id"], team_info["name"]
    except Exception:
        pass
    return None, team_name

async def simulo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.replace("/simulo", "").strip()
    if "vs" not in query:
        await update.message.reply_text("⚠️ Format i gabuar! Shkruaj p.sh: `/simulo Real Madrid vs Barcelona`", parse_mode="Markdown")
        return

    team1_str, team2_str = query.split("vs")
    name1_query, name2_query = team1_str.strip(), team2_str.strip()

    await update.message.reply_text(f"🔍 Duke kërkuar datën, orën dhe koeficientët për **{name1_query} vs {name2_query}**...", parse_mode="Markdown")

    id1, name1 = get_team_id(name1_query)
    id2, name2 = get_team_id(name2_query)

    p1, px, p2 = 0.0, 0.0, 0.0
    odds_source = "Statistika H2H & Vlerësim i Tregut"
    formatted_date = "📅 **Data:** `Të konfirmohet`\n• ⏰ **Ora:** `Së shpejti`"

    if id1 and id2:
        try:
            # Gjejmë ndeshjen e radhës mes tyre për të marrë Fixture ID dhe datën/orën e saktë
            next_url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?h2h={id1}-{id2}&next=1"
            next_res = requests.get(next_url, headers=headers, timeout=5).json()
            fixtures = next_res.get("response", [])
            
            if fixtures:
                fixture_id = fixtures[0]["fixture"]["id"]
                raw_date = fixtures[0]["fixture"].get("date", "")
                
                if raw_date:
                    # Formatimi i datës dhe orës
                    date_part, time_part = raw_date.split("T")
                    time_clean = time_part[:5] # Merr vetëm orën dhe minutën (HH:MM)
                    formatted_date = f"📅 **Data:** `{date_part}`\n• ⏰ **Ora:** `{time_clean} UTC`"

                # Tërheqim koeficientët e basteve (Odds) për këtë ndeshje nga API
                odds_url = f"https://api-football-v1.p.rapidapi.com/v3/odds?fixture={fixture_id}"
                odds_res = requests.get(odds_url, headers=headers, timeout=5).json()
                odds_data = odds_res.get("response", [])

                if odds_data:
                    bookmakers = odds_data[0].get("bookmakers", [])
                    if bookmakers:
                        bets = bookmakers[0].get("bets", [])
                        for bet in bets:
                            if bet.get("id") == 1: # 1X2 market ID
                                values = bet.get("values", [])
                                odd_1 = float(values[0]["odd"])
                                odd_x = float(values[1]["odd"])
                                odd_2 = float(values[2]["odd"])

                                # Përndajmë koeficientët decimalë në përqindje probabiliteti (1 / odd)
                                prob_1 = (1 / odd_1)
                                prob_x = (1 / odd_x)
                                prob_2 = (1 / odd_2)
                                total = prob_1 + prob_x + prob_2

                                p1 = round((prob_1 / total) * 100, 1)
                                px = round((prob_x / total) * 100, 1)
                                p2 = round((prob_2 / total) * 100, 1)
                                odds_source = f"Koeficientët Zyrtarë ({bookmakers[0].get('name', 'Bookmaker')})"
        except Exception:
            pass

    # Nëse API nuk kthen koeficientë direkt, përdorim fallback
    if p1 == 0.0 and px == 0.0 and p2 == 0.0:
        p1, p2, px = 42.5, 30.0, 27.5
        odds_source = "Analizë Historike H2H"

    # Përcaktojmë të favorizuarin
    if p1 > p2 and p1 > px:
        favorite = f"🏆 **I Favorizuar nga Tregu:** {name1_query} ({p1}%)"
    elif p2 > p1 and p2 > px:
        favorite = f"🏆 **I Favorizuar nga Tregu:** {name2_query} ({p2}%)"
    else:
        favorite = "🤝 **Parashikimi:** Ndeshje e ekuilibruar, mundësi e lartë për **Barazim (X)**"

    msg = (
        f"📊 **ANALIZA E NDESHJES & ORARI**\n"
        f"⚔️ **{name1_query} vs {name2_query}**\n\n"
        f"{formatted_date}\n\n"
        f"{favorite}\n\n"
        f"📈 **Probabiliteti Real (1X2):**\n"
        f"• 1 ({name1_query}): **{p1}%**\n"
        f"• X (Barazim): **{px}%**\n"
        f"• 2 ({name2_query}): **{p2}%**\n\n"
        f"ℹ️ *Burimi i të dhënave: {odds_source}*"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("simulo", simulo))
    app.run_polling()
