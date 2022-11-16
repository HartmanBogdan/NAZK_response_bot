import telebot
import requests
import numpy as np
import time
import socket
import ssl
import datetime
import csv

# in TELEGRAM - https://t.me/check_response_bot

bot = telebot.TeleBot("5521564357:AAEyEl6zrML9PGMY-vunQesbEU0d4ZWdw1Y", parse_mode=None)

sitepack = []
sitepack_plus = []
WhileLoopFlag = True
ssl_warning = 0


def time_func():
    return (datetime.datetime.now()).strftime("%d:%m:%y %H:%M:%S")


with open('logout.csv', 'a+', newline='',encoding='utf-8') as csvfile:
    fieldnames = ['Назва операції', 'Результат', 'Час виконання: ДД/ММ/РР Год/Хв/Сек']
    logger = csv.DictWriter(csvfile, fieldnames=fieldnames)
    logger.writeheader()
    logger.writerow({'Назва операції': "Запуск скрипта", 'Результат': " LOADED",
                     'Час виконання: ДД/ММ/РР Год/Хв/Сек': time_func()})


@bot.message_handler(commands=['start'])
def send_welcome(message):
    global sitepack
    global WhileLoopFlag
    sitepack = []
    bot.reply_to(message, "Привіт, тут є два режими як працює цей бот:\n\n"
                          "1)Скинь файл, що називається 'urls.txt', в якому є список посилань(більше 1 посилання) "
                          "розділених між собою переносом строки(ентер на клавіатурі) і бот автоматично буде "
                          "перевіряти всі посилання. \n Щоб зупинити бота - пропиши: "
                          " '/start'.\n\n"
                          "Хочеш скинути новий список в файлі? Спочатку пропиши '/start'"
                          "\n"
                          "\n"
                          "2)Кидай посилання в чат, бот буде записувати їх в список (дублікати ігноруються) та відправ "
                          "+ в чат, щоб почати перевірку цього (окремого)списку. Щоб обнулити список - пропиши "
                          "команду '/clean' \n\n "
                          "Режими незалежні один від одного та можуть працювати паралельно.\n\n"
                          "!!!Вимоги до автоматичної перевірки - /help !!!")

    WhileLoopFlag = False
    logger_writer(first_par="send_welcome(message):Запуск чи перезапуск бота(не скрипта)", sec_par=" LOADED")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
                     "Вимоги до файлу \"urls.txt\":\n"
                     "1) Більше одного посилання на файлі.\n"
                     "2) Посилання починаються з http або https, якщо потрібно перевірити SSL - сертифікат\n"
                     "3) Посилання розділеня між собою переносом строки (Enter)\n"
                     "4) Назва - обов'язково \"urls.txt\"\n"
                     "5) Щоб почати перевірку нового файлу - потрібно спочатку зупинити бота /start ,"
                     "а потім відправити новий файл \"urls.txt\" ")

def logger_writer(first_par, sec_par):
    with open('logout.csv', 'a+', newline='',encoding='utf-8') as csvfile:
        fieldnames = ['Назва операції', 'Результат', 'Час виконання: ДД/ММ/РР Год/Хв/Сек']
        logger = csv.DictWriter(csvfile, fieldnames=fieldnames)
        logger.writerow({'Назва операції': first_par, 'Результат': sec_par,
                         'Час виконання: ДД/ММ/РР Год/Хв/Сек': time_func()})


@bot.message_handler(commands=['clean'])
def clean(message):
    global sitepack_plus
    sitepack_plus = []
    print(sitepack_plus)
    bot.send_message(message.chat.id, "Список запам'ятованих урлів - очищено")
    logger_writer(first_par="Очищення списку запам'ятованих адрес", sec_par=" LOADED  ")


@bot.message_handler(content_types=['document'])
def downloader(message):
    global sitepack
    global WhileLoopFlag
    global logger
    file_name = message.document.file_name
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
        new_file.close()
    sitepack = np.loadtxt("urls.txt", dtype="str")
    print(sitepack)
    print(sitepack.size)
    WhileLoopFlag = True
    while WhileLoopFlag is True:
        loaded = 0
        failed = 0

        try:
            for x in sitepack:
                hostname = x.split("/")
                hostname = hostname[2]
                print(hostname)
                try:
                    requests.get(x)
                    loaded += 1
                    print("send to ssl_check")
                    result_check = ssl_check(x)
                    result_check_days = str(result_check)
                    ssl_alarm_check(message, hostname)
                    logger_writer(first_par='Перевірка з ' + file_name, sec_par=result_check_days + " LOADED  ")
                    print('response from ssl_check')
                except OSError:
                    bot.send_message(message.chat.id, hostname + '  - 🛑FAILURE🛑')
                    logger_writer(first_par='Перевірка з ' + file_name, sec_par=hostname + '  - FAILURE')
                    failed += 1
            # bot.send_message(message.chat.id, str(loaded) + "/" + str(loaded + failed) + " - LOADED ")
            logger_writer(first_par='Перевірка з ' + file_name,
                          sec_par=str(loaded) + "/" + str(loaded + failed) + " - LOADED ")
        except TypeError:
            bot.send_message(message.chat.id,
                             "В файлі лише одне посилання, перезапусти(команда /start) бот та просто скинь посилання "
                             "в чат і натисни + \n TypeError exeption в методі downloader() ")
            logger_writer(first_par='Перевірка з ' + file_name,
                          sec_par="ERROR: В файлі лише одне посилання або помилка зчитування файлу")
        time.sleep(90)


@bot.message_handler(commands=['check_message_urls'])
def check_message_urls(message):
    global sitepack_plus
    loaded = 0
    failed = 0
    #if message.text == "+" and sitepack_plus is not None:


    for x in sitepack_plus:

        try:
            requests.get(x)
            loaded += 1
            result_check = ssl_check(x)
            bot.send_message(message.chat.id, result_check)
            logger_writer(first_par='Перевірка з списку відправлених в чаті посилань.',
                          sec_par=result_check + " - LOADED")

        except OSError:
            hostname = x.split("/")
            hostname = hostname[2]
            bot.send_message(message.chat.id, hostname + "  - 🛑FAILURE🛑")
            logger_writer(first_par='Перевірка з списку відправлених в чаті посилань.',
                          sec_par=hostname + " - FAILURE")
            failed += 1
    bot.send_message(message.chat.id, str(loaded) + "/" + str(loaded + failed) + " - LOADED")
    logger_writer(first_par='Перевірка з списку відправлених в чаті посилань.',
                  sec_par=str(loaded) + "/" + str(loaded + failed) + " - LOADED ")


@bot.message_handler(content_types=['text'])
def add_to_sitepack(message):
    global sitepack_plus
    if message.text.startswith("http") and message.text not in sitepack_plus:
        sitepack_plus.append(message.text)
        logger_writer(first_par='В збережені посилання додано: ',
                      sec_par=message.text)
        print("Збережені посилання:" + str(sitepack_plus))
    try:
        sitepack_plus[0]
    except IndexError:
        bot.send_message(message.chat.id, "Повідомлення не містить посилання на сайт")
        logger_writer(first_par='Перевірка з списку відправлених в чаті посилань.',
                      sec_par=message.text + "  -  Повідомлення не містить посилання на сайт")


def ssl_check(hostname):
    global ssl_warning
    if hostname.startswith("https"):
        print("%s" % hostname)
        hostname = hostname.split("/")
        hostname = hostname[2]
        # https://www.w3schools.com/python/python_datetime.asp
        ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
        context = ssl.create_default_context()
        # to wrap a socket.
        conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=hostname, )
        conn.settimeout(3.0)
        conn.connect((hostname, 443))
        ssl_info = conn.getpeercert()
        Exp_ON = datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
        Days_Remaining = Exp_ON - datetime.datetime.utcnow()
        x = (hostname + " До закінчення сертифікату: " + (str(Days_Remaining).split(" ")[0]) + " днів.")
        print(x)

        conn.close()
        ssl_warning = int(((str(Days_Remaining)).split(" "))[0])
        print(ssl_warning)

        return x
    else:
        hostname = hostname.split("/")
        hostname = hostname[2] + " - не є сайтом, що містить ssl сертифікат."
        return hostname


# перевіряємо ссл дата експайр, якшо менше 10днів - то алармим в чат
def ssl_alarm_check(message, hostname):
    global ssl_warning
    if ssl_warning < 10:
        bot.send_message(message.chat.id,
                         hostname + " --- УВАГА, до закінчення SSL - сертифікату: " + str(ssl_warning) + " днів!!!!")
        logger_writer(first_par="УВАГА!  ",
                      sec_par=hostname + " ---- до закінчення SSL - сертифікату: " + str(ssl_warning) + " днів")

while True:
    try:
        bot.polling(non_stop=True, interval=0)
    except Exception as e:
        print(e)
        logger_writer(first_par= e, sec_par= "     ПОМИЛКА ПІДКЛЮЧЕННЯ")
        time.sleep(5)
        continue
