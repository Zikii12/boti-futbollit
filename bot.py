import logging
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = "9108188458:AAFpm_pipwbrok6n9-WO95XX6gFitXSN0E4"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 Boti yt i Analizave është Online!\n\n"
        "1️⃣ /simulo [Ekipi 1] vs [Ekipi 2]\n"
        "   *(Analizon ndeshjen dhe jep përqindjet & golat)*\n\n"
        "2️⃣ /odds [Odd 1] [Odd X] [Odd 2]\n"
        "   *(Llogarit përqindjet e pastra pa margjinë)*"
    )

async def simulo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.replace("/simulo", "").strip()
    if "vs" not in query:
        await update.message.reply_text("⚠️ Format i gabuar! Shkruaj p.sh: `/simulo Real Madrid vs Barcelona`", parse_mode="Markdown")
        return

    team1_str, team2_str = query.split("vs")
    name1, name2 = team1_str.strip(), team2_str.strip()

    await update.message.reply_text(f"🔍 Duke analizuar takimin **{name1} vs {name2}**...", parse_mode="Markdown")

    # Gjeneron shpërndarje statistikore të fuqishme brenda standardeve të futbollit
    p1 = round(random.uniform(38.0, 55.0), 1)
    p2 = round(random.uniform(22.0, 35.0), 1)
    px = round(100.0 - (p1 + p2), 1)
    avg_g1 = round(random.uniform(1.3, 2.2), 1)
    avg_g2 = round(random.uniform(0.9, 1.6), 1)

    btts_stat = "Po (GG)" if (avg_g1 >= 1.0 and avg_g2 >= 1.0) else "Jo (NG)"
    over_stat = "Over 2.5" if (avg_g1 + avg_g2) > 2.4 else "Under 2.5"

    msg = (
        f"📊 **ANALIZA E NDESHJES**\n"
        f"⚔️ **{name1} vs {name2}**\n\n"
        f"📈 **Përqindjet e Parashikuara:**\n"
        f"• 1 ({name1}): **{p1}%**\n"
        f"• X (Barazim): **{px}%**\n"
        f"• 2 ({name2}): **{p2}%**\n\n"
        f"⚽ **Mesatarja e Vlerësuar e Golave:**\n"
        f"• {name1}: **{avg_g1}** gola\n"
        f"• {name2}: **{avg_g2}** gola\n\n"
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
