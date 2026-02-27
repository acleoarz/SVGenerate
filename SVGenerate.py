import logging
import os
import io
import threading

from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import cairosvg

# --- ЛОГИ ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")

# --- КОМАНДА /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне SVG код или файл .svg, и я превращу его в PNG."
    )

# --- ОБРАБОТКА ТЕКСТА ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "<svg" not in text:
        await update.message.reply_text("Это не похоже на SVG код.")
        return

    try:
        png_bytes = cairosvg.svg2png(bytestring=text.encode("utf-8"))
        await update.message.reply_photo(photo=png_bytes)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Ошибка при конвертации SVG.")

# --- ОБРАБОТКА ФАЙЛОВ ---
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document

    if not document.file_name.endswith(".svg"):
        await update.message.reply_text("Пожалуйста, отправь файл .svg")
        return

    try:
        file = await document.get_file()
        svg_bytes = await file.download_as_bytearray()
        png_bytes = cairosvg.svg2png(bytestring=svg_bytes)
        await update.message.reply_photo(photo=png_bytes)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Ошибка при обработке файла.")

# --- ЗАПУСК БОТА ---
def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    logger.info("Бот запущен...")
    app.run_polling()

# --- FLASK ДЛЯ RENDER FREE ---
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running"

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# --- ЗАПУСК ---
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_flask()
