import logging
import random
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
        "• `/simulo [Ekipi 1] vs [Ekipi 2]` - Analizë e ndeshjes, data, ora dhe koeficientët (1X2)",
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

    msg_status = await update.message.reply_text(f"🔍 Duke përpunuar analizën për **{name1} vs {name2}**...", parse_mode="Markdown")

    formatted_date = "📅 **Data:** `Të konfirmohet`\n• ⏰ **Ora:** `Së shpejti`"
    odds_source = "Analizë e Avancuar e Tregut (H2H & Formë)"
    
    p1, px, p2 = 0.0, 0.0, 0.
