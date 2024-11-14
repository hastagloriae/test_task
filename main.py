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
    for count in range(0, 2):

        sleep(3)
        url = f"https://www.work.ua/resumes-it/?page={count}"

        work_request = requests.get(url, headers=headers)
        soup = BeautifulSoup(work_request.text, "lxml")
        vacancies = soup.find_all("div", class_="card card-hover card-search resume-link card-visited wordwrap")

        for vacancy in vacancies:
            title = vacancy.find('h2').text.strip()
            name = vacancy.find('span', 'strong-600').text.strip()
            link = "https://www.work.ua" + vacancy.find('a')['href']

            yield f"Вакансия: {title}"
            yield f"Имя: {name}"
            yield link

# # Пример использования функции с фильтрацией по должности и местоположению
# for resume_info in get_url():
#     print(resume_info)


for link in get_url():
    work_request = requests.get(link, headers=headers)
    soup = BeautifulSoup(work_request.text, "lxml")
    vacancies = soup.find("div", class_="card wordwrap mt-0")
