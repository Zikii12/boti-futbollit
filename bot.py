import logging
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "9108188458:AAFpm_pipwbrok6n9-WO95XX6gFitXSN0E4"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 Boti yt i Analizave dhe Basteve është gati!\n\n"
        "Mund të përdorësh dy opsionet:\n"
        "1️⃣ /simulo [Ekipi 1] vs [Ekipi 2]\n"
        "   *(Simulon ndeshjen, golat dhe përqindjet)*\n\n"
        "2️⃣ /odds [Odd 1] [Odd X] [Odd 2]\n"
        "   *(Kthen koeficientët e basteve në përqindje reale të tregut)*\n"
        "   Shembull: `/odds 1.90 3.40 4.10`"
    )

async def simulo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    match_query = text.replace("/simulo", "").strip()
    if not match_query:
        match_query = "Ndeshje Analizë"

    golas_1 = random.randint(0, 4)
    golas_2 = random.randint(0, 4)
    total_goals = golas_1 + golas_2

    if golas_1 > golas_2:
        p1 = random.randint(52, 75)
        p2 = random.randint(12, 28)
        draw = 100 - (p1 + p2)
    elif golas_2 > golas_1:
        p2 = random.randint(52, 75)
        p1 = random.randint(12, 28)
        draw = 100 - (p1 + p2)
    else:
        draw = random.randint(35, 55)
        p1 = (100 - draw) // 2
        p2 = 100 - draw - p1

    btts = "Po (GG)" if (golas_1 > 0 and golas_2 > 0) else "Jo (NG)"
    over_2_5 = "Po (Over 2.5)" if total_goals > 2.5 else "Jo (Under 2.5)"

    response = (
        f"📊 **SIMULIMI I NDESHJES:** {match_query}\n\n"
        f"⚽ **Rezultati i Parashikuar:** {golas_1} - {golas_2}\n\n"
        f"📈 **Probabiliteti:**\n"
        f"• 1 (Vendasit): **{p1}%**\n"
        f"• X (Barazim): **{draw}%**\n"
        f"• 2 (Mysafirët): **{p2}%**\n\n"
        f"💡 **Treguesit:**\n"
        f"• Të dyja shënojnë (BTTS): **{btts}**\n"
        f"• Gola total (>2.5): **{over_2_5}**"
    )
    await update.message.reply_text(response, parse_mode="Markdown")

async def odds_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("⚠️ Përdorim i gabuar! Shkruaj p.sh: `/odds 1.90 3.40 4.10`", parse_mode="Markdown")
            return

        o1 = float(args[0])
        ox = float(args[1])
        o2 = float(args[2])

        # Llogaritja e probabilitetit të papërpunuar
        prob1 = (1 / o1) * 100
        probx = (1 / ox) * 100
        prob2 = (1 / o2) * 100
        
        total_prob = prob1 + probx + prob2
        margin = total_prob - 100 # Margjina e bastores (Overround)

        # Përqindjet e pastra (duke hequr margjinën)
        real_p1 = (prob1 / total_prob) * 100
        real_px = (probx / total_prob) * 100
        real_p2 = (prob2 / total_prob) * 100

        response = (
            f"🧮 **ANALIZA E KOEFICIENTEVE (ODDS):**\n\n"
            f"• Koeficientët: **1({o1}) | X({ox}) | 2({o2})**\n\n"
            f"📊 **Përqindjet reale të tregut (Pa Margjinë):**\n"
            f"• 1: **{real_p1:.1f}%**\n"
            f"• X: **{real_px:.1f}%**\n"
            f"• 2: **{real_p2:.1f}%**\n\n"
            f"⚠️ **Margjina e Bastores (Fitimi i tyre):** `{margin:.2f}%`"
        )
        await update.message.reply_text(response, parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("⚠️ Ju lutem vendosni numra të vlefshëm! P.sh: `/odds 1.90 3.40 4.10`", parse_mode="Markdown")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("simulo", simulo))
    app.add_handler(CommandHandler("odds", odds_calc))
    print("Boti i avancuar po punon...")
    app.run_polling()