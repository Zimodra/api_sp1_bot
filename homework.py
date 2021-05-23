import os
import time

import requests
import telegram
from dotenv import load_dotenv
import logging

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
    name_file = name.split('__')[0]
    homework_name = name_file.split('.')[0]
    status = homework.get('status')
    if status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif status == 'reviewing':
        verdict = 'Работа взята в ревью.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    api = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    params = {'from_date': current_timestamp}
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    homework_statuses = requests.get(api, params=params, headers=headers)
    if homework_statuses:
        return homework_statuses.json()
    return {}

def send_message(message, bot_client):
    return bot_client.send_message(CHAT_ID, message)
    logging.info('Сообщение отправлено')


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date', current_timestamp)  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            message = f'Бот столкнулся с ошибкой: {e}'
            logging.error(message)
            send_message(message)
            time.sleep(5)


if __name__ == '__main__':
    main()
