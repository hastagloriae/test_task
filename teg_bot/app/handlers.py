from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import teg_bot.app.keyboards as kb
from parsing.main import ResumeScraper  # Импортируем парсера для резюме

router = Router()

# Хранилище для данных пользователя (например, текущий сайт и фильтры)
user_data = {}


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Приветствие при запуске бота."""
    await message.answer(f'Привет, {message.from_user.first_name}!\n'
                         f'Тебя приветствует парсинг бот, здесь ты можешь найти вакансии ИТ-специалистов.'
                         f'\nЧтобы узнать более детальную информацию по поводу того, как использовать бот, нажми /help')


@router.message(Command('help'))
async def get_help(message: Message):
    """Инструкция по использованию бота."""
    await message.answer(
        'Этот бот работает следующим образом:\n'
        '1. Выбираешь сайт для парсинга (work.ua или robota.ua).\n'
        '2. Настроишь фильтры для поиска вакансий (должность, город, опыт и т.д.).\n'
        '3. Запустишь парсинг и получишь список резюме, соответствующих твоим фильтрам.\n'
        'Чтобы приступить, нажми /start_parsing.'
    )


@router.message(Command('start_parsing'))
async def start_parsing(message: Message):
    """Запуск парсинга, выбор сайта."""
    await message.answer('Выберите сайт для парсинга вакансий.', reply_markup=kb.setting)


@router.message(F.text == 'Work.ua')
async def work_ua(message: Message):
    """Выбор сайта work.ua."""
    user_data[message.from_user.id] = {'site': 'work.ua'}
    await message.answer('Вы выбрали Work.ua. Теперь выберите фильтры для поиска вакансий.',
                         reply_markup=kb.job_filters)


@router.message(F.text == 'Robota.ua')
async def robota_ua(message: Message):
    """Выбор сайта robota.ua."""
    user_data[message.from_user.id] = {'site': 'robota.ua'}
    await message.answer('Вы выбрали Robota.ua. Теперь выберите фильтры для поиска вакансий.',
                         reply_markup=kb.job_filters)


@router.message(F.text == 'Назад к выбору сайта')
async def back_to_site(message: Message):
    """Возврат к выбору сайта."""
    await message.answer('Выберите сайт для парсинга вакансий.', reply_markup=kb.setting)


@router.message(F.text == 'Должность')
async def set_position(message: Message):
    """Настройка должности для поиска."""
    user_data[message.from_user.id]['position'] = message.text  # Сохраняем должность
    await message.answer('Введите должность для поиска.')


@router.message(F.text == 'Город')
async def set_city(message: Message):
    """Настройка города для поиска."""
    user_data[message.from_user.id]['city'] = message.text  # Сохраняем город
    await message.answer('Введите город для поиска.')


@router.message(F.text == 'Тип занятости')
async def set_employment_type(message: Message):
    """Настройка типа занятости."""
    user_data[message.from_user.id]['employment_type'] = message.text  # Сохраняем тип занятости
    await message.answer('Введите тип занятости для поиска (например, "полная" или "неполная" занятость).')


@router.message(F.text == 'Опыт работы')
async def set_experience(message: Message):
    """Настройка опыта работы для поиска."""
    user_data[message.from_user.id]['experience'] = message.text  # Сохраняем опыт работы
    await message.answer('Введите опыт работы для поиска.')


@router.message(F.text == 'Скиллы')
async def set_skills(message: Message):
    """Настройка навыков для поиска."""
    user_data[message.from_user.id]['skills'] = message.text  # Сохраняем навыки
    await message.answer('Введите требуемые навыки для поиска.')


# Следует собрать и отфильтровать все параметры перед запуском парсинга
@router.message(F.text == 'Запуск парсинга')
async def start_parsing_process(message: Message):
    """Запуск парсинга с учетом выбранных фильтров."""
    filters = {
        'position': user_data[message.from_user.id].get('position'),
        'city': user_data[message.from_user.id].get('city'),
        'employment_type': user_data[message.from_user.id].get('employment_type'),
        'experience': user_data[message.from_user.id].get('experience'),
        'skills': user_data[message.from_user.id].get('skills')
    }

    # Получаем список кандидатов с выбранного сайта
    scraper = ResumeScraper(base_url="https://www.work.ua/resumes-it", headers={}, filters_vacancy=filters, filters_score={})
    sorted_resumes = scraper.scrape_resumes(pages=5)  # Собираем данные с нескольких страниц

    if sorted_resumes:
        # Если есть резюме, отправляем их пользователю
        for resume in sorted_resumes:
            message_text = (
                f"Вакансия: {resume['title']}\n"
                f"Имя: {resume['name']}\n"
                f"Город: {resume['Город']}\n"
                f"Возраст: {resume['Возраст']}\n"
                f"Занятость: {resume['Занятость']}\n"
                f"Навыки: {resume['Навыки']}\n"
                f"Опыт: {resume['Опыт']}\n"
                f"Ссылка: {resume['link']}\n"
                f"Баллы: {resume.get('score', 'Не оценено')}\n"
                "-" * 40
            )
            await message.answer(message_text)
    else:
        await message.answer('По вашему запросу не найдено резюме.')
