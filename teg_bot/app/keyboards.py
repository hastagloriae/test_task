from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Обычная клавиатура для выбора сайта
setting = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Work.ua')],
        [KeyboardButton(text='Robota.ua')],
        [KeyboardButton(text='Назад к выбору сайта')]
    ],
    resize_keyboard=True
)

# Обычная клавиатура для фильтров
job_filters = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Должность')],
        [KeyboardButton(text='Город')],
        [KeyboardButton(text='Тип занятости')],
        [KeyboardButton(text='Опыт работы')],
        [KeyboardButton(text='Ключевые навыки')],
        [KeyboardButton(text='Начать парсинг')]
    ],
    resize_keyboard=True
)

# Основная клавиатура с несколькими кнопками
main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Catalog')],
        [KeyboardButton(text='Trash'), KeyboardButton(text='Contacts')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Select a menu item.'
)

# Инлайн клавиатура для ссылок на сайты
inline_setting = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Work.ua', url='https://www.work.ua/resumes-it')],
        [InlineKeyboardButton(text='Robota.ua', url='https://robota.ua/candidates/all/ukraine?rubrics=%5B%221%22%5D')]
    ]
)
