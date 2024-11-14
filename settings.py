import requests
from bs4 import BeautifulSoup
from time import sleep

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/"
                  "537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}


def get_url():
    for count in range(0, 1):
        sleep(3)
        url = f"https://www.work.ua/resumes-it/?page={count}"

        work_request = requests.get(url, headers=headers)
        soup = BeautifulSoup(work_request.text, "lxml")
        vacancies = soup.find_all("div", class_="card card-hover card-search resume-link card-visited wordwrap")

        for vacancy in vacancies:
            title = vacancy.find('h2').text.strip()
            name = vacancy.find('span', 'strong-600').text.strip()
            link = "https://www.work.ua" + vacancy.find('a')['href']
            yield {"title": title, "name": name, "link": link}


def other_info(resume_link):
    response = requests.get(resume_link, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    # Ищем информацию по меткам: город, возраст и занятость
    info = {
        "Город": "Город не найден",
        "Возраст": "Возраст не найден",
        "Занятость": "Занятость не найдена"
    }

    # Находим метки и значения для каждой категории
    city_label = soup.find("dt", string=lambda x: x and ("місто" in x.lower() or "місто проживання" in x.lower()))
    if city_label:
        info["Город"] = city_label.find_next_sibling("dd").text.strip()

    age_label = soup.find("dt", string="Вік:")
    if age_label:
        info["Возраст"] = age_label.find_next_sibling("dd").text.strip()

    employment_label = soup.find("dt", string="Зайнятість:")
    if employment_label:
        info["Занятость"] = employment_label.find_next_sibling("dd").text.strip()

    return info


for resume in get_url():
    print(f"Вакансия: {resume['title']}")
    print(f"Имя: {resume['name']}")
    print(f"Ссылка: {resume['link']}")

    # Переход на страницу резюме для получения дополнительной информации
    additional_info = other_info(resume['link'])
    print(f"Город: {additional_info['Город']}")
    print(f"Возраст: {additional_info['Возраст']}")
    print(f"Занятость: {additional_info['Занятость']}\n")
