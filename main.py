import requests
from bs4 import BeautifulSoup
import re
from time import sleep


class ResumeParser:
    def __init__(self, base_url, headers, filters=None):
        self.base_url = base_url
        self.headers = headers
        self.filters = filters if filters else {}

    def get_url(self, page=0):
        """Получение всех вакансий с указанной страницы."""
        url = f"{self.base_url}?page={page}"
        sleep(3)  # Чтобы избежать блокировки за частые запросы
        work_request = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(work_request.text, "lxml")
        return soup.find_all("div", class_="card card-hover card-search resume-link card-visited wordwrap")

    def parse_resume(self, vacancy):
        """Парсинг информации о вакансии."""
        title = vacancy.find('h2').text.strip()
        name = vacancy.find('span', 'strong-600').text.strip()
        link = "https://www.work.ua" + vacancy.find('a')['href']
        return {"title": title, "name": name, "link": link}

    def other_info(self, resume_link):
        """Получение дополнительной информации о кандидате с полной страницы."""
        response = requests.get(resume_link, headers=self.headers)
        soup = BeautifulSoup(response.text, "lxml")

        info = {
            "Город": "Город не найден",
            "Возраст": "Возраст не найден",
            "Занятость": "Занятость не найдена",
            "Навыки": "",
            "Опыт": ""
        }

        # Поиск информации по меткам
        info = {
            "Город": "Город не найден",
            "Возраст": "Возраст не найден",
            "Занятость": "Занятость не найдена",
            "Навыки": "Навыки не найдены",
            "Опыт": "Опыт не найден"
        }

        # Город
        city_label = soup.find("dt", string=lambda x: x and ("місто" in x.lower() or "місто проживання" in x.lower()))
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

        # Опыт работы(оставлю как есть ибо на ворк нету отдельной графы на самой странице вакансии)
        experience_label = soup.find("dt", string="Досвід роботи:")
        if experience_label:
            experience_value = experience_label.find_next_sibling("dd")
            if experience_value:
                info["Опыт"] = experience_value.text.strip()

        # Возвращаем собранную информацию
        return info

    def matches_keywords_in_resume(self, resume_link):
        """Проверка, содержат ли ключевые слова в тексте резюме (описание, опыт и т.д.)."""
        response = requests.get(resume_link, headers=self.headers)
        soup = BeautifulSoup(response.text, "lxml")

        # Собираем весь текст с резюме
        text_to_check = soup.get_text().lower()

        # Проходим по ключевым словам и проверяем, присутствуют ли они в тексте
        keywords = [kw.lower() for kw in self.filters.get("keywords", [])]
        for keyword in keywords:
            if keyword not in text_to_check:
                return False  # Если хотя бы одно ключевое слово не найдено, пропускаем это резюме
        return True  # Если все ключевые слова найдены

    def matches_filters(self, resume):
        """Проверка, подходит ли резюме под фильтры."""
        # Проверяем основные фильтры
        if self.filters.get("job_position") and self.filters["job_position"].lower() not in resume["title"].lower():
            return False
        if self.filters.get("city") and self.filters["city"].lower() not in resume.get("Город", "").lower():
            return False
        if self.filters.get("employment_type") and self.filters["employment_type"].lower() not in resume.get("Занятость", "").lower():
            return False
        if self.filters.get("min_salary") and int(resume.get("Зарплата", 0)) < self.filters["min_salary"]:
            return False
        if self.filters.get("min_experience") and int(resume.get("Опыт", 0)) < self.filters["min_experience"]:
            return False

        # Проверка ключевых слов непосредственно на странице с полным резюме
        if not self.matches_keywords_in_resume(resume['link']):
            return False

        return True


class ResumeScraper:
    def __init__(self, base_url, headers, filters=None):
        self.parser = ResumeParser(base_url, headers, filters)

    def scrape_resumes(self, pages=1):
        """Парсинг резюме с нескольких страниц с фильтрацией."""
        all_resumes = []
        for page in range(pages):
            vacancies = self.parser.get_url(page)
            for vacancy in vacancies:
                resume_info = self.parser.parse_resume(vacancy)
                additional_info = self.parser.other_info(resume_info['link'])
                if additional_info:
                    resume_info.update(additional_info)
                    # Применяем фильтры
                    if self.parser.matches_filters(resume_info):
                        all_resumes.append(resume_info)
        return all_resumes


# Основной код для парсинга
if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/"
                      "537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    base_url = "https://www.work.ua/resumes-it"  # Базовый URL для работы с резюме

    # Фильтры для парсинга
    filters = {
        "job_position": "",  # Фильтровать по должности
        "min_experience": 0,                 # Минимум 2 года опыта
        "city": "",                      # Фильтровать по городу
        "employment_type": "",      # Фильтровать по типу занятости
        "min_salary": 0,                  # Минимальная зарплата 1000
        "keywords": [""]  # Ключевые слова для поиска
    }

    scraper = ResumeScraper(base_url, headers, filters)

    # Собираем резюме с указанной страницы(с 1 и до указанной) 3(в коде)=2(на сайте)
    resumes = scraper.scrape_resumes(pages=3)

    # Выводим результаты
    for resume in resumes:
        print(f"Вакансия: {resume['title']}")
        print(f"Имя: {resume['name']}")
        print(f"Город: {resume['Город']}")
        print(f"Возраст: {resume['Возраст']}")
        print(f"Занятость: {resume['Занятость']}")
        print(f"Навыки: {resume['Навыки']}")
        print(f"Опыт: {resume['Опыт']}")
        print(f"Ссылка: {resume['link']}\n")
