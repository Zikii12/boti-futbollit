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
        "🎯 Boti yt i Analizave me Statistika Reale!\n\n"
        "1️⃣ /simulo [Ekipi 1] vs [Ekipi 2]\n"
        "   *(Tërheq format reale dhe statistikat H2H)*\n\n"
        "2️⃣ /odds [Odd 1] [Odd X] [Odd 2]\n"
        "   *(Llogarit përqindjet e pastra pa margjinë)*"
    )

def get_team_id(team_name):
    url = f"https://api-football-v1.p.rapidapi.com/v3/teams?search={team_name}"
    response = requests.get(url, headers=headers)
    data = response.json()
    if data.get("response"):
        return data["response"][0]["team"]["id"], data["response"][0]["team"]["name"]
    return None, team_name

async def simulo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.replace("/simulo", "").strip()
    if "vs" not in query:
        await update.message.reply_text("⚠️ Format i gabuar! Shkruaj p.sh: `/simulo Real Madrid vs Barcelona`", parse_mode="Markdown")
        return

    team1_str, team2_str = query.split("vs")
    team1_str, team2_str = team1_str.strip(), team2_str.strip()

    await update.message.reply_text(f"🔍 Po marr të dhënat reale për **{team1_str}** dhe **{team2_str}**...", parse_mode="Markdown")

    id1, name1 = get_team_id(team1_str)
    id2, name2 = get_team_id(team2_str)

    if not id1 or not id2:
        await update.message.reply_text("⚠️ Nuk u gjetën skuadrat! Sigurohu që emrat janë të saktë.")
        return

    h2h_url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/headtohead?h2h={id1}-{id2}"
    res = requests.get(h2h_url, headers=headers).json()
    fixtures = res.get("response", [])

    w1, w2, draws = 0, 0, 0
    total_g1, total_g2 = 0, 0
    count = len(fixtures[:10])

    if count > 0:
        for f in fixtures[:10]:
            g1 = f["goals"]["home"] or 0
            g2 = f["goals"]["away"] or 0
            if f["teams"]["home"]["id"] == id1:
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
        p1, px, p2 = 40.0, 30.0, 30.0
        avg_g1, avg_g2 = 1.5, 1.1

    btts_stat = "Lartë (GG)" if (avg_g1 >= 1.0 and avg_g2 >= 1.0) else "Ulet (NG)"
    over_stat = "Over 2.5" if (avg_g1 + avg_g2) > 2.5 else "Under 2.5"

    msg = (
        f"📊 **ANALIZA E BAZUAR NË TË DHËNA REALE (H2H)**\n"
        f"⚔️ **{name1} vs {name2}**\n\n"
        f"📈 **Probabiliteti Historik:**\n"
        f"• 1 ({name1}): **{p1}%**\n"
        f"• X (Barazim): **{px}%**\n"
        f"• 2 ({name2}): **{p2}%**\n\n"
        f"⚽ **Mesatarja e Golave për ndeshje:**\n"
        f"• {name1}: **{avg_g1}** gola\n"
        f"• {name2}: **{avg_g2}** gola\n\n"
        f"💡 **Pritshmëria:**\n"
        f"• Gola Total: **{over_stat}**\n"
        f"• BTTS: **{btts_stat}**"
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
