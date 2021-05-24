import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv
from telegram.error import TelegramError

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


def parse_homework_status(homework):
    name = homework.get('homework_name')
    if name is None:
        text = 'Проект не найден'
        logging.error(text)
        return text
    name_file = name.split('__')[0]
    homework_name = name_file.split('.')[0]
    status = homework.get('status')
    if status is None:
        text = 'Статус не найден'
        logging.error(text)
        return text
    status_list = {
        'rejected': 'К сожалению в работе нашлись ошибки.',
        'reviewing': 'Работа взята в ревью.',
        'approved': ('Ревьюеру всё понравилось, '
                     'можно приступать к следующему уроку.')
    }
    verdict = status_list.get(status)
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    api = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    params = {'from_date': current_timestamp or int(time.time())}
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    try:
        homework_statuses = requests.get(api, params=params, headers=headers)
    except requests.exceptions.RequestException as e:
        message = f'Бот столкнулся с ошибкой: {e}'
        logging.error(message)
        send_message(message)
    if homework_statuses:
        return homework_statuses.json()
    return {}


def send_message(message, bot_client):
    try:
        telegram_message = bot_client.send_message(CHAT_ID, message)
        logging.info('Сообщение отправлено')
        return telegram_message
    except TelegramError as e:
        text = f'Бот столкнулся с ошибкой: {e}'
        logging.error(text)
        send_message(text)


def main():
    telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]
                ))
            current_timestamp = new_homework.get(
                'current_date', current_timestamp
            )
            time.sleep(300)

        except Exception as e:
            message = f'Бот столкнулся с ошибкой: {e}'
            logging.error(message)
            send_message(message)
            time.sleep(5)


if __name__ == '__main__':
    main()
