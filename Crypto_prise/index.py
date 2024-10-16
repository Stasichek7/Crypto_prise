import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# URLs для запитів до CoinGecko API
COIN_LIST_URL = 'https://api.coingecko.com/api/v3/coins/list'
PRICE_URL = 'https://api.coingecko.com/api/v3/simple/price'

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функція для отримання списку всіх доступних криптовалют
def get_crypto_list():
    try:
        response = requests.get(COIN_LIST_URL)
        response.raise_for_status()
        return response.json()  # Повертаємо список криптовалют
    except requests.RequestException as e:
        logger.error(f"Помилка запиту списку криптовалют: {e}")
        return None

# Функція для отримання ціни криптовалюти через API CoinGecko
def fetch_crypto_price(crypto_id: str):
    try:
        response = requests.get(f'{PRICE_URL}?ids={crypto_id}&vs_currencies=usd')
        response.raise_for_status()
        data = response.json()
        return data.get(crypto_id, {}).get('usd')
    except requests.RequestException as e:
        logger.error(f"Помилка запиту ціни: {e}")
        return None

# Обробник повідомлень для отримання ціни криптовалюти
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    crypto_name = update.message.text.strip().lower()
    logger.info(f"Користувач запросив ціну для: {crypto_name}")

    # Отримуємо список криптовалют
    coin_list = get_crypto_list()
    if not coin_list:
        await update.message.reply_text('Не вдалося отримати список криптовалют. Спробуйте пізніше.')
        return

    # Знаходимо відповідну криптовалюту в списку
    crypto_id = next((coin['id'] for coin in coin_list if coin['symbol'] == crypto_name or coin['name'].lower() == crypto_name), None)

    if not crypto_id:
        await update.message.reply_text(f'Не знайдено криптовалюту з назвою або символом "{crypto_name}".')
        return

    # Отримуємо ціну криптовалюти
    price = fetch_crypto_price(crypto_id)

    if price is not None:
        await update.message.reply_text(f'Ціна {crypto_name.capitalize()} зараз: ${price}')
    else:
        await update.message.reply_text(f'Не вдалося знайти інформацію про криптовалюту {crypto_name}. Перевірте назву.')

# Обробник для команди /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привіт! Введіть назву криптовалюти, щоб отримати її поточну ціну.'
    )

# Основна функція для запуску бота
if __name__ == '__main__':
    # Створення додатку з вашим токеном бота
    application = ApplicationBuilder().token('7388192040:AAE6ySUHROsj21UOZkSxs4uOmdVnRrKTmC4').build()

    # Додаємо обробник для команди /start
    application.add_handler(CommandHandler("start", start_command))

    # Додаємо обробник повідомлень для запиту цін криптовалют
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бот
    application.run_polling()
