import os
import cairosvg
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь SVG файл — я конвертирую его в PNG.")

async def handle_svg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document

    if not document or document.mime_type != "image/svg+xml":
        await update.message.reply_text("Это не SVG файл.")
        return

    file = await document.get_file()
    await file.download_to_drive("input.svg")

    cairosvg.svg2png(url="input.svg", write_to="output.png")

    with open("output.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)

    os.remove("input.svg")
    os.remove("output.png")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_svg))

    print("Bot started...")
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
