import requests
from bs4 import BeautifulSoup
from sorter import Sorter


class ResumeParser:
    def __init__(self, headers):
        self.headers = headers
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_url(self, base_url, page=0):
        """Получение всех вакансий с указанной страницы."""
        url = f"{base_url}?page={page}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            return soup.find_all("div", class_="card card-hover card-search resume-link card-visited wordwrap")
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе {url}: {e}")
            return []

    def parse_resume(self, vacancy):
        """Парсинг информации о вакансии."""
        try:
            title = vacancy.find('h2').text.strip()
            name = vacancy.find('span', 'strong-600').text.strip()
            link = "https://www.work.ua" + vacancy.find('a')['href']
            return {"title": title, "name": name, "link": link}
        except AttributeError:
            return {}

    def other_info(self, resume_link):
        """Получение дополнительной информации о кандидате с полной страницы."""
        try:
            response = self.session.get(resume_link)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            info = {
                "Город": "Город не найден",
                "Возраст": "Возраст не найден",
                "Занятость": "Занятость не найдена",
                "Навыки": "",
                "Опыт": ""
            }

            # Поиск информации по меткам
            city_label = soup.find("dt",
                                   string=lambda x: x and ("місто" in x.lower() or "місто проживання" in x.lower()))
            if city_label:
                city_value = city_label.find_next_sibling("dd")
                if city_value:
                    info["Город"] = city_value.text.strip()

            # Возраст
            age_label = soup.find("dt", string="Вік:")
            if age_label:
                age_value = age_label.find_next_sibling("dd")
                if age_value:
                    info["Возраст"] = age_value.text.strip()

            # Занятость
            employment_label = soup.find("dt", string="Зайнятість:")
            if employment_label:
                employment_value = employment_label.find_next_sibling("dd")
                if employment_value:
                    info["Занятость"] = employment_value.text.strip()

            # Навыки
            skills_label = soup.find("ul", class_="list-unstyled my-0 flex flex-wrap")
            if skills_label:
                skills_text = skills_label.get_text(separator=", ", strip=True)
                if skills_text:
                    info["Навыки"] = skills_text

            # Опыт работы
            experience_label = soup.find("dt", string="Досвід роботи:")
            if experience_label:
                experience_value = experience_label.find_next_sibling("dd")
                if experience_value:
                    info["Опыт"] = experience_value.text.strip()

            return info
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе {resume_link}: {e}")
            return {}


class ResumeFilter:
    def __init__(self, filters):
        self.filters = filters

    def matches_filters(self, resume):
        """Проверка, подходит ли резюме под фильтры поиска."""
        for key, value in self.filters.items():
            if value:
                resume_value = resume.get(key, "")

                # Если значение resume_value - это список, обрабатываем его иначе
                if isinstance(resume_value, list):
                    resume_value = " ".join(resume_value)  # Объединяем элементы списка в строку

                # Если значение фильтра - список, проверяем все его элементы
                if isinstance(value, list):
                    for v in value:
                        if isinstance(resume_value, str) and v.lower() not in resume_value.lower():
                            return False
                else:
                    # Если значение фильтра - строка, проверяем, содержит ли строка значение в нижнем регистре
                    if isinstance(resume_value, str) and value.lower() not in resume_value.lower():
                        return False

        return True


class ResumeScraper:
    def __init__(self, base_url, headers, filters_vacancy=None, filters_score=None):
        self.base_url = base_url
        self.parser = ResumeParser(headers)
        self.filter_vacancy = ResumeFilter(filters_vacancy)
        self.filter_score = ResumeFilter(filters_score) if filters_score else None

    def scrape_resumes(self, pages=1):
        """Парсинг резюме с нескольких страниц с фильтрацией по обязательным параметрам."""
        all_resumes = []
        for page in range(pages):
            vacancies = self.parser.get_url(self.base_url, page)
            for vacancy in vacancies:
                resume_info = self.parser.parse_resume(vacancy)
                if resume_info:
                    additional_info = self.parser.other_info(resume_info['link'])
                    if additional_info:
                        resume_info.update(additional_info)
                        if self.filter_vacancy.matches_filters(resume_info):
                            all_resumes.append(resume_info)
        return all_resumes


if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/"
                      "537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    base_url = "https://www.work.ua/resumes-it"  # Базовый URL для работы с резюме

    # фильтры для парсинга резюме
    filters_vacancy = {
        "job_position": "",  # Фильтровать по должности
        "keywords": [""],  # Ключевые слова для поиска
        "city": "",  # Фильтровать по городу
        "employment_type": "",  # Фильтровать по типу занятости
    }

    # фильтры для сортировки
    filters_score = {
        "job_position": "web",  # Фильтровать по должности
        "keywords": ["disinger", "HTML", "CSS"],  # Ключевые слова для поиска
        "city": "Київ",  # Фильтровать по городу
        "employment_type": None,  # Фильтровать по типу занятости
    }

    scraper = ResumeScraper(base_url, headers, filters_vacancy, filters_score)

    # Собираем резюме с 10 страниц
    resumes = scraper.scrape_resumes(pages=5)

    # Создаем экземпляр Sorter и сортируем кандидатов
    sorter = Sorter(filters_score)
    sorted_resumes = sorter.sort_candidates(resumes)

    # Выводим результаты
    for i, resume in enumerate(sorted_resumes, 1):
        print(f"Кандидат {i}:")
        print(f"Вакансия: {resume['title']}")
        print(f"Имя: {resume['name']}")
        print(f"Город: {resume['Город']}")
        print(f"Возраст: {resume['Возраст']}")
        print(f"Занятость: {resume['Занятость']}")
        print(f"Навыки: {resume['Навыки']}")
        print(f"Опыт: {resume['Опыт']}")
        print(f"Ссылка: {resume['link']}")
        print(f"Баллы: {resume.get('score', 'Не оценено')}")
        print("-" * 40)
