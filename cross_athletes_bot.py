import pandas as pd
# pyTelegramBotAPI
import telebot
from telebot import types
import sqlite3
from datetime import datetime, timedelta
import os

# accesses_info
from accesses_storage import bot_id, list_of_admins

# Создаем бота
bot = telebot.TeleBot(bot_id)

# id admin
primary_id_admin = list_of_admins


#---------------------------------------------------обработка команды /help----------------------------------------------------
# обработка команды /admin
@bot.message_handler(commands=["help"])
def admin_message(message, res=False):
    answer = '''
Привет, этот бот создан для удобства и автоматизации взаимодействия тренера и атлетов.

Команды:

/start - команда для атлетов
    - Количество тренировок, оставшися у атлетов.
    - Статистика по посещениям (в разработке)
    - Рейтинг атлетов (в разработке)

/admin - команда для тренера
    - Добавление атлета
    - Добавление пакетов тренировок для атлетов
    - Отметка атлетов на тренировке
    - Удаление атлета (в разработке)
    - Выгрузка всей базы данных в excel

Вопросы и предложения сюда https://t.me/Sergeymasl
    '''


    bot.send_message(message.chat.id, answer)



#---------------------------------------------------обработка команды /admin----------------------------------------------------


# обработка команды /admin
@bot.message_handler(commands=["admin"])
def admin_message(message, res=False):
    answer = "Выберите команду, милорд"
    # создаем кнопки по добавлению пользователя, добавление пакетов тренировок, отметить пользователей на тернировке,
    # удалить пользователя, выгрузке базы

    markup = ''
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Добавить атлета', callback_data='insert_user'))
    markup.add(types.InlineKeyboardButton('Добавить пакет тренировок атлету', callback_data='add_a_training_package'))
    markup.add(types.InlineKeyboardButton('Отметить атлета на тренировке', callback_data='add_workout'))
    #markup.add(types.InlineKeyboardButton('Удалить пользователя', callback_data='drop_user'))
    markup.add(types.InlineKeyboardButton('Выгрузить базу в excel', callback_data='get_database'))

    bot.send_message(message.chat.id, answer, reply_markup=markup)



#---------- кнопка добавление пользователя

@bot.callback_query_handler(func=lambda x: x.data == 'insert_user')
def insert_user(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    # проверка на id amin
    if int(callback_query.from_user.id) in primary_id_admin:
        # 1 шаг
        message_to_insert_user_1 = bot.send_message(callback_query.from_user.id, "Введите имя")
        bot.register_next_step_handler(message_to_insert_user_1, insert_user_1)
    else:
        bot.send_message(callback_query.from_user.id, "Ты не админ")
        for admin in primary_id_admin:
            bot.send_message(admin, f'user {callback_query.from_user.username} c id {callback_query.from_user.id} пытается добавить пользователя')

# 2 шаг
def insert_user_1(message_from_insert_user):
    # получаем имя
    globals()['name_isert_user'] = message_from_insert_user.text
    message_to_insert_user_2 = bot.send_message(message_from_insert_user.chat.id, "Введите фамилию")
    bot.register_next_step_handler(message_to_insert_user_2, insert_user_2)

# 3 шаг
def insert_user_2(message_from_insert_user_1):
    # получаем фамилию
    globals()['surname_isert_user'] = message_from_insert_user_1.text
    # добавляем в базу данных пользователя
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO users (fname, sname)
    VALUES
    ('{name_isert_user}', '{surname_isert_user}');
    ''')
    conn.commit()
    conn.close()
    bot.send_message(message_from_insert_user_1.chat.id, f"Атлет {name_isert_user} {surname_isert_user} добавлен")



#---------- добавление пакетов тренировок

@bot.callback_query_handler(func=lambda x: x.data == f'add_a_training_package')
def add_packages(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    if int(callback_query.from_user.id) in primary_id_admin:
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        result = cursor.execute('SELECT fname, sname FROM users').fetchall()
        markup = ''
        markup=types.InlineKeyboardMarkup()
        # выгружаем всех пользователей из БД и просим выбрать
        for i, name in enumerate(result):
            locals()[f'item{i}'] = types.InlineKeyboardButton(f"{name[0]} {name[1]}", callback_data = f'add packages to user user selection >{name[0]} {name[1]}<')
            markup.add(locals()[f'item{i}'])
        conn.close()
        bot.send_message(callback_query.from_user.id, f'Кому добавляем?', reply_markup=markup)

    else:
        bot.send_message(callback_query.from_user.id, "Ты не админ")
        for admin in primary_id_admin:
            bot.send_message(admin, f'user {callback_query.from_user.username} c id {callback_query.from_user.id} пытается добавить пакет тренировок')


# отлавливаем добавление пакетов тренировок

@bot.callback_query_handler(func=lambda x: x.data.rfind('add packages to user user selection') >= 0)
def add_packages_to_user_user_selection(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    fname = callback_query.data[callback_query.data.find('>')+1:callback_query.data.find('<')].split()[0]
    sname = callback_query.data[callback_query.data.find('>')+1:callback_query.data.find('<')].split()[1]
    markup = ''
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('10 тренировок / 45 дней', callback_data=f'add packages to user add package >{fname} {sname}<10'))
    markup.add(types.InlineKeyboardButton('5 тренировок / 30 дней', callback_data=f'add packages to user add package >{fname} {sname}<5'))
    bot.send_message(callback_query.from_user.id, 'Какой пакет?', reply_markup=markup)


# добавляем пакет
@bot.callback_query_handler(func=lambda x: x.data.rfind('add packages to user add package') >= 0)
def add_packages_to_user_add_package(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    # отлавливаем параметры
    fname = callback_query.data[callback_query.data.find('>')+1:callback_query.data.find('<')].split()[0]
    sname = callback_query.data[callback_query.data.find('>')+1:callback_query.data.find('<')].split()[1]
    package = callback_query.data[callback_query.data.find('<')+1:]
    if package == '5':
        days_for_delta = 30
        package_name = '5 тренировок / 30 дней'
    elif package == '10':
        days_for_delta = 45
        package_name = '10 тренировок / 45 дней'

    # добавляем в пакет в БД
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    pri_user_id = cursor.execute(f'SELECT pri_user_id FROM users WHERE fname = "{fname}" AND sname = "{sname}"').fetchone()[0]
    # дата начала действия пакета
    # если пакетов нет, ставим дату внесения
    # если пакеты есть ставим - дата истечения последнего пакета + 1
    if cursor.execute(f'SELECT pri_packages_id FROM packages WHERE pri_user_id = {pri_user_id}').fetchone() == None:
        date_begin = datetime.now()
    else:
        str_to_date = cursor.execute(f'SELECT MAX(date_final) FROM packages WHERE pri_user_id = {pri_user_id}').fetchone()[0]
        date_begin = datetime.strptime(str_to_date,'%Y-%m-%d') + timedelta(days = 1)

    date_final = date_begin + timedelta(days = days_for_delta)

    cursor.execute(f'''
    INSERT INTO packages (pri_user_id, package, date_begin, date_final, quantity_left, quantity_begin)
    VALUES (
            {pri_user_id},
            "{package_name}",
            "{str(date_begin.date())}",
            "{str(date_final.date())}",
            {int(package)},
            {int(package)})
    ''')
    conn.commit()
    conn.close()
    bot.send_message(callback_query.from_user.id, 'Добавлено')


#---------- отметить пользователя на тренировке

# запрос кого отметить
@bot.callback_query_handler(func=lambda x: x.data == 'add_workout')
def add_workout(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    # проверка на id admin
    if int(callback_query.from_user.id) in primary_id_admin:
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        # проверяем чтобы были пакеты тренировок и отсеиваем кому уже отметили тренировку
        result = cursor.execute(f'''
            SELECT fname, sname
            FROM users
            WHERE pri_user_id NOT IN (
                SELECT pri_user_id
                FROM traning
                WHERE date_trening = "{str(datetime.now().date())}"
                )
            AND pri_user_id IN (
            SELECT DISTINCT pri_user_id
            FROM packages
            WHERE quantity_left > 0
            AND
            julianday(date_final) >= julianday('now')
            )
            ''').fetchall()

        # если нет пользователей с пакетами тренировок
        if len(result) == 0:
            bot.send_message(callback_query.from_user.id, f'Ни у одного атлета нет пакетов тренировок или все атлеты уже отмечены')
        # если есть
        else:
            markup = ''
            markup=types.InlineKeyboardMarkup()
            # выгружаем всех пользователей из БД и просим выбрать
            for i, name in enumerate(result):
                locals()[f'item{i}'] = types.InlineKeyboardButton(f"{name[0]} {name[1]}", callback_data = f'add workout for >{name[0]} {name[1]}<')
                markup.add(locals()[f'item{i}'])
            conn.close()
            bot.send_message(callback_query.from_user.id, f'Кого отметить?', reply_markup=markup)

    else:
        bot.send_message(callback_query.from_user.id, "Ты не админ")
        for admin in primary_id_admin:
            bot.send_message(admin, f'user {callback_query.from_user.username} c id {callback_query.from_user.id} пытается отметить пользователя на тренировке')

#отлавливает кого отмечаем и зацикливаем
@bot.callback_query_handler(func=lambda x: x.data.rfind('add workout for') >= 0)
def add_workout_for(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    # отлавливаем параметры
    fname = callback_query.data[callback_query.data.find('>')+1:callback_query.data.find('<')].split()[0]
    sname = callback_query.data[callback_query.data.find('>')+1:callback_query.data.find('<')].split()[1]
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute(f'''
    INSERT INTO traning(pri_user_id, date_trening)
    SELECT pri_user_id, "{str(datetime.now().date())}" as date
    FROM users WHERE fname = "{fname}" AND sname = "{sname}";''')
    conn.commit()
    cursor.execute(f'''
    UPDATE packages SET quantity_left = quantity_left - 1
    WHERE pri_user_id IN (SELECT pri_user_id FROM users WHERE fname = "{fname}" AND sname = "{sname}")
    AND julianday(date_final) >= julianday('now')
    AND julianday(date_begin) <= julianday('now');
    ''')
    conn.commit()
    conn.close()
    markup = ''
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Отметить еще одного', callback_data='add_workout'))
    bot.send_message(callback_query.from_user.id, "Добавлено", reply_markup=markup)


#---------- удалить пользователя

    #-----------------------------------------------------------------НЕ ПРОРАБОТАНО



#---------- выгрузка базы

@bot.callback_query_handler(func=lambda x: x.data == f'get_database')
def get_database(callback_query: types.CallbackQuery):
    # проверка на id amin
    if int(callback_query.from_user.id) in primary_id_admin:
        bot.answer_callback_query(callback_query.id)
        conn = con = sqlite3.connect('test.db')
        for table in pd.read_sql('SELECT name FROM sqlite_master WHERE type ="table"',con = conn)['name'].to_list():
            # выгрузка
            pd.read_sql(f'SELECT * FROM {table}',con = conn).to_excel(f'{table}.xlsx', index = False)
            doc = open(f'{table}.xlsx', 'rb')
            bot.send_document(callback_query.from_user.id, doc)
            doc.close()
            os.remove(f'{table}.xlsx')
        conn.close()
    else:
        bot.send_message(callback_query.from_user.id, "Ты не админ")
        for admin in primary_id_admin:
            bot.send_message(admin, f'user {callback_query.from_user.username} c id {callback_query.from_user.id} пытается выгрузить базу')


#---------------------------------------------------обработка команды /start----------------------------------------------------

@bot.message_handler(commands=["start"])
def start_message(message, res=False):
    answer = "Привет, выбирай команды:"
    # создаем кнопки "сколько у меня осталось тренировок"
    markup = ''
    markup=types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Посмотреть сколько тренировок у меня осталось', callback_data=f'how many workouts do I have'))

    bot.send_message(message.chat.id, answer, reply_markup=markup)



#---------- отработка кнопки "сколько у меня осталось тренировок"

@bot.callback_query_handler(func=lambda x: x.data == f'how many workouts do I have')
def select_workouts(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    conn = sqlite3.connect('test.db')
    users_id_list = pd.read_sql('SELECT DISTINCT user_id FROM users',con = conn)['user_id'].to_list()
    # проверка на наличие id в таблице users
    # если есть, отправляем сколько осталось тренировок
    if int(callback_query.from_user.id) in users_id_list:
        # проверка на наличие пакетов тренировок
        df_if_user_id_in_packages = pd.read_sql(
            f'SELECT * FROM packages as p LEFT JOIN users as u USING (pri_user_id) WHERE u.user_id = {int(callback_query.from_user.id)}',
            con = conn)
        if int(callback_query.from_user.id) in df_if_user_id_in_packages['user_id'].to_list():
            message_trening = f"У вас {df_if_user_id_in_packages['quantity_left'].sum()} тренировок, из них:"
            for index in df_if_user_id_in_packages.index:
                message_trening += f"\n{df_if_user_id_in_packages.loc[index, 'quantity_left']} тренировок до {df_if_user_id_in_packages.loc[index, 'date_final']}"
            bot.send_message(callback_query.from_user.id, message_trening)
            conn.close()

        else:
            bot.send_message(callback_query.from_user.id, 'У вас нет тренировок', reply_markup=markup)
            conn.close()
    # если нет, то просим выбрать себя для добления в БД
    else:
        cursor = conn.cursor()
        result = cursor.execute('SELECT fname, sname FROM users WHERE user_id IS NULL').fetchall()
        markup = ''
        markup=types.InlineKeyboardMarkup()
        # выгружаем всех пользователей из БД и просим выбрать
        for i, name in enumerate(result):
            locals()[f'item{i}'] = types.InlineKeyboardButton(f"{name[0]} {name[1]}", callback_data = f'add user_id to user >{name[0]} {name[1]}<')
            markup.add(locals()[f'item{i}'])
        conn.close()
        # кнопка о том что пользователя нет
        markup.add(types.InlineKeyboardButton('меня нет в этом списке', callback_data = f'user doest find himself>{name[0]} {name[1]}<'))
        bot.send_message(callback_query.from_user.id, 'Я еще не знаю вас, выберите себя', reply_markup=markup)

#отлавливаем нажатие кнопки с выбором пользователя и добавляем в БД
@bot.callback_query_handler(func=lambda x: x.data.rfind('add user_id to user') >= 0)
def add_user_id(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    # вытаскиваем имя и фамилию из data
    fname = callback_query.data[callback_query.data.find('>')+1:callback_query.data.find('<')].split()[0]
    sname = callback_query.data[callback_query.data.find('>')+1:callback_query.data.find('<')].split()[1]
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    # заносим ip user в базу данных
    cursor.execute(
        f'''
        UPDATE users SET user_id = {int(callback_query.from_user.id)} WHERE fname = "{fname}" AND sname = "{sname}"

        ''')
    conn.commit()
    # выведим количество тренировок
    # проверка на наличие пакетов тренировок
    bot.send_message(callback_query.from_user.id, f'я добавил вас в базу данных, теперь при каждом запросе я буду знать что вы {fname} {sname}')
    df_if_user_id_in_packages = pd.read_sql(
        f'SELECT * FROM packages as p LEFT JOIN users as u USING (pri_user_id) WHERE u.user_id = {int(callback_query.from_user.id)}',
        con = conn)
    if int(callback_query.from_user.id) in df_if_user_id_in_packages['user_id'].to_list():
        message_trening = f"У вас {df_if_user_id_in_packages['quantity_left'].sum()} тренировок, из них:"
        for index in df_if_user_id_in_packages.index:
            message_trening += f"\n{df_if_user_id_in_packages.loc[index, 'quantity_left']} тренировок до {df_if_user_id_in_packages.loc[index, 'date_final']}"
        bot.send_message(callback_query.from_user.id, message_trening)
        conn.close()
    else:
        bot.send_message(callback_query.from_user.id, 'У вас нет тренировок')
        conn.close()


# отработка когда пользователя не нашел себя в БД
@bot.callback_query_handler(func=lambda x: x.data.rfind('user doest find himself') >= 0)
def user_doest_find_himself(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    fname = callback_query.data[callback_query.data.find('>')+1:callback_query.data.find('<')].split()[0]
    sname = callback_query.data[callback_query.data.find('>')+1:callback_query.data.find('<')].split()[1]
    # оправляем пользователю ответ о том что его еще не добавили
    bot.send_message(callback_query.from_user.id, f'хмм, я написал о вас админу. Либо он вас еще не добавил. Либо и вовсе не знает о вас...\U0001F937')
    # отправляем сообщение админам
    for admin in primary_id_admin:
        bot.send_message(admin, f'Милорд, {fname} {sname} не нашел/ла себя в списке атлетов, добавьте или напишите ему. Его user_name - "{callback_query.from_user.username}"')



#------------------------------------------------------ЗАПУСК БОТА-------------------------------------------------------------

# Запускаем бота
bot.polling(none_stop=True, interval=0)