import os
import cairosvg
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь мне SVG файл — я конвертирую его в PNG.")

# обработка SVG
async def handle_svg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document

    if document.mime_type != "image/svg+xml":
        await update.message.reply_text("Это не SVG файл.")
        return

    file = await document.get_file()
    svg_path = "input.svg"
    png_path = "output.png"

    await file.download_to_drive(svg_path)

    # конвертация SVG → PNG
    cairosvg.svg2png(url=svg_path, write_to=png_path)

    # отправка результата
    await update.message.reply_photo(photo=open(png_path, "rb"))

    os.remove(svg_path)
    os.remove(png_path)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.ALL, handle_svg))

print("Bot started...")
app.run_polling()
