import telebot
import requests
from telebot import types
from sdamgia import SdamGIA
from random import randint
#Вот это нужно для .env, если будешь использовать токен напрямую, можешь удалить
from dotenv import load_dotenvn
import os
load_dotenv()
TOKEN = os.getenv('TOKEN')
#================================================================================

# Если у тебя токен наприямую, тогда
TOKEN = "YOU_TOKEN_BOT" #сюда токен

# Инициализация SdamGIA
sdamgia = SdamGIA()

 # Замените на ваш токен бота
bot = telebot.TeleBot(TOKEN)


zadanija = {1: 1,
            2: 1,
            3: 1,
            4: 1,
            5: 1,
            6: 1,
            7: 1,
            8: 1,
            9: 1,
            10: 1,
            11: 1,
            12: 1,
            13: 1,
            14: 1,
            15: 1,
            16: 1,
            17: 1,
            18: 1,
            19: 1,
            20: 1,
            21: 1,
            22: 1,
            23: 1,} #Это сколько и каких заданий будет генерироваться в пдф



# Сопоставление названий предметов с их кодами
subject_mapping = {
    #"Матем.Профиль": "math", "Матем.База": "mathb",   #С математикой пока проблемы, так как я не понял как у них нумерованы задания и простой рандомайзер не находит
    "Физика": "phys", "Информатика": "inf",
    "Русский": "rus", "Биология": "bio",
    "Английский язык": "en", "Немецкий язык": "de",
    "Французский язык": "fr", "Испанский язык": "sp",
    "Литература": "lit", "Химия": "chem",
    "География": "geo", "Общество": "soc", "История": "hist"
}

user_subjects = {} #Хранит данные о предмете и юзере

# Функция для создания главного меню
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Получить задание")
    btn2 = types.KeyboardButton("Найти ответ")
    btn4 = types.KeyboardButton("Сгенерировать вариант")
    btn3 = types.KeyboardButton("Изменить предмет")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# Функция для создания клавиатуры выбора предмета
def get_subjects_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for subject in subject_mapping.keys():
        markup.add(types.KeyboardButton(subject))
    return markup


@bot.message_handler(func=lambda message: message.text == "Изменить предмет" or message.text == "/start") 
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = list(subject_mapping.keys())
    for button in buttons:
        markup.add(types.KeyboardButton(button))
    bot.send_message(message.chat.id, "Выберите предмет:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in subject_mapping)
def handle_subject_selection(message):
    user_id = message.from_user.id
    subject = subject_mapping[message.text]
    user_subjects[user_id] = subject  # Запоминаем выбранный предмет
    bot.send_message(message.chat.id, f"Вы выбрали предмет: {message.text}", reply_markup=main_menu())


@bot.message_handler(func=lambda message: message.text == "Сгенерировать вариант")
def varian_generating(message):
    user_id = message.from_user.id
    subject = user_subjects.get(user_id)

    if subject is not None:
        # Отправляем сообщение о начале генерации
        sent_message = bot.send_message(message.chat.id, "Генерирую вариант...")

        # Генерируем вариант и PDF
        generate_variant = sdamgia.generate_test(subject, zadanija)
        pdf = sdamgia.generate_pdf(subject, generate_variant, pdf='h')

        # Редактируем предыдущее сообщение с результатами
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=sent_message.message_id,
            text=f"Ваш вариант №{generate_variant}\n\n[Открыть содержимое варианта]({pdf})\n\nУзнать ответы вы можете по ссылке [НАЖМИ](https://{subject}-ege.sdamgia.ru/test?id={generate_variant}&print=true)",
            parse_mode='Markdown'
        )
    else:
        bot.send_message(message.chat.id, "У вас еще нет выбранного предмета. Пожалуйста, выберите предмет с помощью кнопок.")


@bot.message_handler(func=lambda message: message.text == "Получить задание" or message.text == "/get")
def get_subject(message):
    user_id = message.from_user.id
    subject = user_subjects.get(user_id)

    if subject:
        while True:  # Цикл для поиска валидного задания
            task_id = randint(5, 10000)  # Генерируем новый task_id
            problem = sdamgia.get_problem_by_id(subject, task_id)

            if problem and 'condition' in problem:
                condition_text = problem['condition']['text']  # Извлекаем условие
                resheb_text = problem['solution']['text']  # Извлекаем решение
                photos = problem['condition'].get('images') # Фот из условия
                answer = problem['answer'] # Короткий ответ

                # Если в задании есть фото, оно его отправит
                if photos:
                    photo_url = photos[0] if isinstance(photos, list) and photos else photos
                    try:
                        response = requests.get(photo_url)
                        if response.status_code == 200:
                            bot.send_photo(message.chat.id, response.content)
                        else:
                            bot.send_message(message.chat.id,
                                             f"Не удалось загрузить фото. Код ошибки: {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        bot.send_message(message.chat.id, f"Произошла ошибка при попытке загрузить фото: {e}")

                # Отправляем условие и решение независимо от наличия изображения
                bot.send_message(
                    message.chat.id,
                    f"<a href='https://{subject}-ege.sdamgia.ru/problem?id={task_id}'>Вопрос № {task_id}</a>\n\n{condition_text}\n\nОтвет: <tg-spoiler>{resheb_text}\n\nКороткий ответ: {answer}</tg-spoiler>\n\nДля получение следущего задание напишите /get",
                    parse_mode='HTML'
                )

                break  # Выходим из цикла, если проблема найдена
    else:
        bot.send_message(message.chat.id,
                         "У вас еще нет выбранного предмета. Пожалуйста, выберите предмет с помощью кнопок или напишите /start")




@bot.message_handler(func=lambda message: message.text == "Найти ответ")
def get_random_variant(message):
    user_id = message.from_user.id
    subject = user_subjects.get(user_id)

    if subject:
        bot.send_message(message.chat.id,
                         "Пожалуйста, отправьте *полное* условие задачи, если условие не полное, то результатов будет не более 15",
                         parse_mode='Markdown')
        bot.register_next_step_handler(message, process_condition)
    else:
        bot.send_message(message.chat.id,
                         "У вас еще нет выбранного предмета. Пожалуйста, выберите предмет с помощью кнопок или напишите /start")


def process_condition(message):
    user_id = message.from_user.id
    subject = user_subjects.get(user_id)
    request = message.text  # Сохраняем условие задачи

    # Выполняем поиск по условию
    results = sdamgia.search(subject, request)
    request1 = request.replace(' ', '+')

    # Ограничиваем количество результатов до 20
    if results:
        for result in results[:15]:  # Используем срез для получения первых 20 результатов
            problem = sdamgia.get_problem_by_id(subject, result)
            resheb_text = problem['condition']['text']
            answer_text = problem['answer']
            bot.send_message(
                message.chat.id,
                f'[Ответ №{result} на сайте](https://{subject}-ege.sdamgia.ru/problem?id={result})\n\n{resheb_text}\n*Ответ:* {answer_text}',
                parse_mode='Markdown'
            )

        # Отправляем 21-е сообщение
        bot.send_message(message.chat.id, f'Больше на сайте: https://{subject}-ege.sdamgia.ru/search?search={request1}')
    else:
        bot.send_message(message.chat.id, "К сожалению, ничего не найдено по вашему запросу.")


# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)
