import logging
import os
import io
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import cairosvg

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен берём из переменной окружения
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN не найден. Добавь его в Environment Variables на Render.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне SVG код или файл .svg, и я превращу его в PNG картинку."
    )

async def handle_svg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    svg_code = update.message.text

    try:
        if "<svg" not in svg_code.lower():
            await update.message.reply_text("Это не похоже на SVG код.")
            return

        png_data = cairosvg.svg2png(bytestring=svg_code.encode("utf-8"))

        await update.message.reply_photo(
            photo=io.BytesIO(png_data),
            caption="Вот твоя картинка!"
        )

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("Ошибка при обработке SVG.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        document = update.message.document

        if not document.file_name.lower().endswith(".svg"):
            await update.message.reply_text("Пожалуйста, отправь файл в формате .svg")
            return

        file = await document.get_file()
        file_bytes = await file.download_as_bytearray()
        svg_code = file_bytes.decode("utf-8")

        png_data = cairosvg.svg2png(bytestring=svg_code.encode("utf-8"))

        await update.message.reply_photo(
            photo=io.BytesIO(png_data),
            caption="Вот твоя картинка из файла!"
        )

    except Exception as e:
        logger.error(f"Ошибка с файлом: {e}")
        await update.message.reply_text("Не могу обработать этот файл.")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_svg))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
