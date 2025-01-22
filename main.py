from db_init import create_tables
from telebot import types
from repository import Repository
import telebot
import config
from datetime import datetime, timedelta

user_state = {}

create_tables()

bot = telebot.TeleBot(config.SECRET_KEY)

repo = Repository()

@bot.message_handler(commands=['start'])
def start(message):
    repo.create_user(message.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    butt2 = types.KeyboardButton('Добавить задачу➕')
    butt4 = types.KeyboardButton('Просмотреть задачи📃')
    butt5 = types.KeyboardButton('Что ты можешь❓')
    keyboard.add( butt2, butt5,butt4)
    bot.send_message(message.chat.id,'Привет, я твой ежедневник✌️ ',reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == 'Добавить задачу➕')
def create_task(message):
    user_state[message.chat.id] = {'state': 'creating_task', 'task': {}}
    bot.send_message(message.chat.id,'Напишите имя задачи')
    bot.register_next_step_handler(message, process_name_step)
def process_name_step(message):
    name = message.text
    user_state[message.chat.id]['task']['name'] = name
    bot.send_message(message.chat.id, f'Напишите описание задачи "{name}"')
    bot.register_next_step_handler(message, process_desc_step)
def process_desc_step(message):
    desc = message.text
    user_state[message.chat.id]['task']['desc'] = desc
    bot.send_message(message.chat.id, 'Напишите дату выполнения задачи(пример ГОД-МЕС-ДЕНЬ ЧАС:МИН)')
    bot.register_next_step_handler(message, process_dedl_step)

def process_dedl_step(message):
    dedl = message.text
    user_state[message.chat.id]['task']['dedl'] = dedl
    bot.send_message(message.chat.id, 'Задача сохранена')
    repo.create_task(message.chat.id, user_state[message.chat.id]['task']['name'],
                     user_state[message.chat.id]['task']['desc'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                     user_state[message.chat.id]['task']['dedl'])
    del user_state[message.chat.id]



@bot.message_handler(func=lambda message: message.text == 'Просмотреть задачи📃')
def get_all_tasks(message,page=0):
    buttons_per_page = 5
    bot.send_message(message.chat.id, 'Ваши задачи',
                     reply_markup=generate_markup(buttons_per_page, message.chat.id, page))
def generate_markup(buttons_per_page, user_id, page=0):
    markup = types.InlineKeyboardMarkup()

    # Получаем задачи для текущей страницы
    offset = buttons_per_page * page
    all_tasks = repo.get_tasks_by_user_id(user_id, buttons_per_page, offset)

    # Создаем кнопки для задач
    for task in all_tasks:
        name = task[0]  # Имя задачи
        markup.add(types.InlineKeyboardButton(text=f'{name}', callback_data=f'task_{name}'))

    # Добавляем кнопки навигации
    navigation = []
    if page > 0:  # Кнопка "назад", если это не первая страница
        navigation.append(types.InlineKeyboardButton('⬅️', callback_data=f'page_{page - 1}'))

    if len(all_tasks) == buttons_per_page:  # Кнопка "вперед", если есть больше задач
        navigation.append(types.InlineKeyboardButton('➡️', callback_data=f'page_{page + 1}'))

    if navigation:
        markup.add(*navigation)

    return markup

@bot.message_handler(func=lambda message: message.text == 'Что ты можешь❓')
def function_of_bot(message):
    bot.send_message(message.chat.id,'Я могу добавить задачу,удалить ее. Также буду напоминать о ней')


@bot.callback_query_handler(func=lambda call:True)
def handler_callback(call):
    if call.data.startswith('task'):
        print(user_state)
        print(call.from_user.id)
        print(call.message.chat.id)
        task = call.data.split('_')[1]
        other = repo.get_by_name(task)
        print(other)
        user_state[call.from_user.id] = {
             'state':'update', 'task': {'name': task}
        }
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Удалить задачу❌', callback_data='delete_word'))
        markup.add(types.InlineKeyboardButton(text='Выполнено✅',callback_data='compl'))
        bot.send_message(call.message.chat.id, f'Название: {task}\nОписание: {other[0][0]}\nДата выполнения: {other[0][1]}', reply_markup=markup)
    if call.data == 'delete_word':
        #user_state[call.from_user.id][''] = 'delete_word'
        repo.delete_task(user_state[call.from_user.id]['task']['name'],call.from_user.id)
        del user_state[call.message.chat.id]
        bot.send_message(call.message.chat.id,'Задача была удалена')
    if call.data == 'compl':
        repo.status_change(call.from_user.id,user_state[call.from_user.id]['task']['name'])
        bot.send_message(call.message.chat.id, 'Задача выполнена')
    if call.data.startswith('page_'):
        page = int(call.data.split('_')[1])
        buttons_per_page = 5
        bot.edit_message_reply_markup(call.message.chat.id,call.message.message_id,reply_markup=generate_markup(buttons_per_page,call.from_user.id,page))








bot.polling()