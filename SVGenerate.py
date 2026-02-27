import os
import asyncio
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

    await update.message.reply_photo(photo=open("output.png", "rb"))

    os.remove("input.svg")
    os.remove("output.png")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_svg))

    print("Bot started...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
