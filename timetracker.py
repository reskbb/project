import sqlite3
from datetime import datetime, timedelta
import time
import requests
import config
from config import SECRET_KEY

BOT_TOKEN = SECRET_KEY
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_telegram_message(chat_id, text):
    """
    Отправка сообщения пользователю в Telegram.

    Args:
        chat_id (int): ID чата пользователя (уникальный идентификатор Telegram пользователя).
        text (str): Сообщение, которое будет отправлено пользователю.
    """
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        # Отправляем POST-запрос к Telegram API для отправки сообщения
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Проверка на успешный запрос
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке сообщения: {e}")


def check_deadlines():
    """
    Проверка дедлайнов в базе данных и отправка напоминаний пользователям.

    Алгоритм:
    1. Устанавливаем соединение с базой данных.
    2. Проверяем записи, у которых дедлайн наступит через 2 минуты (или менее).
    3. Отправляем напоминание пользователю.
    4. Обновляем статус задачи как "уведомление отправлено" (поле notified = 1).
    """
    try:
        # Подключаемся к базе данных
        with sqlite3.connect("database.db") as conn:
            print('Подключение')
            cursor = conn.cursor()

            # Получаем текущее время
            now = datetime.now()
            # Вычисляем время через 2 минуты
            two_minutes_later = now + timedelta(minutes=15)

            # Ищем задачи, у которых дедлайн наступает через 15 минуты и уведомления еще не отправлялись
            cursor.execute("""
            SELECT id, user_id, name, deadline
            FROM tasks
            WHERE notified = 0 AND datetime(deadline) BETWEEN ? AND ?
            """, (now.strftime("%Y-%m-%d %H:%M:%S"), two_minutes_later.strftime("%Y-%m-%d %H:%M:%S")))
            print('поиск задачи')
            print(now.strftime("%Y-%m-%d %H:%M:%S"), two_minutes_later.strftime("%Y-%m-%d %H:%M:%S"))
            tasks = cursor.fetchall()
            print(f"Найдено задач: {len(tasks)}")
            for task in tasks:
                print(f"Задача ID: {task[0]}, Пользователь ID: {task[1]}, Дедлайн: {task[2]}")

            print('перед отправкой')
            # Проходим по каждой задаче, соответствующей критериям
            for task_id, user_id, name, deadline in tasks:
                # Отправляем уведомление пользователю
                print("отправлять начинаю")
                send_telegram_message(user_id, f"Напоминание! Срок выполнения вашей задачи {name} наступит в {deadline}.")
                print('сообщение отправлено',task_id,deadline,user_id)
                # Обновляем статус задачи в базе данных (уведомление отправлено)
                cursor.execute("UPDATE tasks SET notified = 1 WHERE id = ?", (task_id,))

            # Фиксируем изменения в базе данных
            conn.commit()
    except sqlite3.DatabaseError as e:
        print(f"Ошибка базы данных: {e}")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")


if __name__ == "__main__":
    """
    Основной цикл программы:
    1. Постоянно проверяет дедлайны с интервалом 1 минута.
    2. Вызывает функцию проверки дедлайнов (check_deadlines).
    """
    while True:
        # Проверяем дедлайны
        check_deadlines()
        # Ожидаем 60 секунд перед следующей проверкой
        time.sleep(60)