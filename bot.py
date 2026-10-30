import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = "9108188458:AAFpm_pipwbrok6n9-WO95XX6gFitXSN0E4"
RAPIDAPI_KEY = "1b41bb4863msh3e2bc115ca860d2p152e5cjsn03752bc6a9ad"

headers = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 Boti i Analizave me Të Dhëna Reale H2H!\n\n"
        "1️⃣ /simulo [Ekipi 1] vs [Ekipi 2]\n"
        "   *(Tërheq ndeshjet direkte dhe statistikat reale)*\n\n"
        "2️⃣ /odds [Odd 1] [Odd X] [Odd 2]\n"
        "   *(Llogarit përqindjet e pastra dhe margjinën)*"
    )

def get_team_id(team_name):
    try:
        url = f"https://api-football-v1.p.rapidapi.com/v3/teams?search={team_name}"
        response = requests.get(url, headers=headers, timeout=6)
        data = response.json()
        if data.get("response"):
            team_info = data["response"][0]["team"]
            return team_info["id"], team_info["name"]
    except Exception as e:
        print(T gabim te get_team_id: {e})
    return None, team_name

async def simulo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.replace("/simulo", "").strip()
    if "vs" not in query:
        await update.message.reply_text("⚠️ Format i gabuar! Shkruaj p.sh: `/simulo Real Madrid vs Barcelona`", parse_mode="Markdown")
        return

    team1_str, team2_str = query.split("vs")
    name1_query, name2_query = team1_str.strip(), team2_str.strip()

    await update.message.reply_text(f"🔍 Duke kërkuar të dhënat reale për **{name1_query}** dhe **{name2_query}**...", parse_mode="Markdown")

    id1, name1 = get_team_id(name1_query)
    id2, name2 = get_team_id(name2_query)

    if not id1 or not id2:
        await update.message.reply_text(
            f"⚠️ Nuk u gjetën ID-të për skuadrat në API-Football!\n"
            f"Provo t'i shkruash emrat në anglisht (p.sh. `Real Madrid`, `Barcelona`, `Milan`, `Inter`)."
        )
        return

    # Tërheqim ndeshjet direkte (H2H)
    try:
        h2h_url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/headtohead?h2h={id1}-{id2}"
        res = requests.get(h2h_url, headers=headers, timeout=6).json()
        fixtures = res.get("response", [])
    except Exception:
        fixtures = []

    w1, w2, draws = 0, 0, 0
    total_g1, total_g2 = 0, 0
    count = len(fixtures[:10])

    if count > 0:
        for f in fixtures[:10]:
            goals = f.get("goals", {})
            g1 = goals.get("home") or 0
            g2 = goals.get("away") or 0
            
            teams = f.get("teams", {})
            home_team_id = teams.get("home", {}).get("id")

            if home_team_id == id1:
                total_g1 += g1
                total_g2 += g2
                if g1 > g2: w1 += 1
                elif g2 > g1: w2 += 1
                else: draws += 1
            else:
                total_g1 += g2
                total_g2 += g1
                if g2 > g1: w1 += 1
                elif g1 > g2: w2 += 1
                else: draws += 1

        p1 = round((w1 / count) * 100, 1)
        p2 = round((w2 / count) * 100, 1)
        px = round((draws / count) * 100, 1)
        avg_g1 = round(total_g1 / count, 1)
        avg_g2 = round(total_g2 / count, 1)
    else:
        # Nëse nuk ka ndeshje H2H direkte të regjistruara në databazë
        await update.message.reply_text(f"⚠️ U gjetën skuadrat ({name1} & {name2}), por s'ka mjaftueshëm ndeshje direkte H2H në arkivë.")
        return

    btts_stat = "Po (GG)" if (avg_g1 >= 1.0 and avg_g2 >= 1.0) else "Jo (NG)"
    over_stat = "Over 2.5" if (avg_g1 + avg_g2) > 2.4 else "Under 2.5"

    msg = (
        f"📊 **ANALIZA E BAZUAR NË H2H REAL**\n"
        f"⚔️ **{name1} vs {name2}**\n\n"
        f"📈 **Statistikat e Ndeshjeve Direkte (Fundit {count}):**\n"
        f"• Fitore {name1}: **{p1}%** ({w1} ndeshje)\n"
        f"• Barazime: **{px}%** ({draws} ndeshje)\n"
        f"• Fitore {name2}: **{p2}%** ({w2} ndeshje)\n\n"
        f"⚽ **Mesatarja e Golave në H2H:**\n"
        f"• {name1}: **{avg_g1}** gola/ndeshje\n"
        f"• {name2}: **{avg_g2}** gola/ndeshje\n\n"
        f"💡 **Sugjerime / Vlera:**\n"
        f"• Gola Total: **{over_stat}**\n"
        f"• Të dyja shënojnë (BTTS): **{btts_stat}**"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def odds_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("⚠️ Përdorim i gabuar! Shkruaj: `/odds 1.90 3.40 4.10`", parse_mode="Markdown")
            return

        o1, ox, o2 = float(args[0]), float(args[1]), float(args[2])
        prob1, probx, prob2 = (1/o1)*100, (1/ox)*100, (1/o2)*100
        total_prob = prob1 + probx + prob2
        margin = total_prob - 100

        msg = (
            f"🧮 **ANALIZA E KOEFICIENTEVE (ODDS):**\n\n"
            f"📊 **Përqindjet Reale të Tregut:**\n"
            f"• 1: **{(prob1/total_prob)*100:.1f}%**\n"
            f"• X: **{(probx/total_prob)*100:.1f}%**\n"
            f"• 2: **{(prob2/total_prob)*100:.1f}%**\n\n"
            f"⚠️ **Margjina e Bastores:** `{margin:.2f}%`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("⚠️ Vendosni numra të vlefshëm!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("simulo", simulo))
    app.add_handler(CommandHandler("odds", odds_calc))
    app.run_polling()
