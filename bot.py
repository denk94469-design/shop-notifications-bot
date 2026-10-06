import os
import logging
from html import escape
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_IDS = [int(x.strip()) for x in os.getenv("OWNER_IDS", "").split(",") if x.strip()]
logging.basicConfig(format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", level=logging.INFO)

def is_owner(update: Update) -> bool:
    return bool(update.effective_user and update.effective_user.id in OWNER_IDS)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update): return
    await update.message.reply_text("🛒 <b>Магазин повідомлення</b>\n\n🔐 Доступ підтверджено.\n👥 Ви є одним із власників бота.\n\n📦 Нові замовлення із сайту будуть надходити сюди автоматично.", parse_mode="HTML")

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        await update.message.reply_text(f"Ваш Telegram ID: <code>{update.effective_user.id}</code>", parse_mode="HTML")

def build_order_message(order: dict) -> str:
    def e(key, default="—"): return escape(str(order.get(key, default)))
    return ("🛍️ <b>НОВЕ ЗАМОВЛЕННЯ</b>\n"
            f"🆔 <b>Замовлення:</b> #{e('order_id')}\n"
            f"📅 <b>Час:</b> {e('created_at')}\n\n"
            "📦 <b>ТОВАР</b>\n"
            f"• Назва: <b>{e('product')}</b>\n• Кількість: <b>{e('quantity')} шт.</b>\n• Ціна: <b>{e('price')}</b>\n• Сума: <b>{e('total')}</b>\n\n"
            "🚚 <b>ДОСТАВКА</b>\n"
            f"• Спосіб: <b>{e('delivery')}</b>\n• Відділення / пункт: <b>{e('branch')}</b>\n• Місто: <b>{e('city')}</b>\n• Адреса: <b>{e('address')}</b>\n\n"
            "👤 <b>ОТРИМУВАЧ</b>\n"
            f"• Ім'я: <b>{e('name')}</b>\n• Прізвище: <b>{e('surname')}</b>\n• Телефон: <b>{e('phone')}</b>\n\n"
            "🔔 <i>Замовлення отримано із сайту.</i>")

async def send_order(order: dict) -> bool:
    if not BOT_TOKEN: raise RuntimeError("BOT_TOKEN не налаштовано.")
    if not OWNER_IDS: raise RuntimeError("OWNER_IDS не налаштовано.")
    app = Application.builder().token(BOT_TOKEN).build()
    await app.initialize(); await app.start()
    try:
        message = build_order_message(order)
        for owner_id in OWNER_IDS:
            await app.bot.send_message(chat_id=owner_id, text=message, parse_mode="HTML", disable_web_page_preview=True)
    finally:
        await app.stop(); await app.shutdown()
    return True

def create_application():
    if not BOT_TOKEN: raise RuntimeError("Не задано BOT_TOKEN у .env")
    if not OWNER_IDS: raise RuntimeError("Не задано OWNER_IDS у .env")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", id_command))
    return app

if __name__ == "__main__":
    app = create_application()
    print("🛒 Магазин повідомлення: бот запущено.")
    print(f"👥 Дозволених власників: {len(OWNER_IDS)}")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
