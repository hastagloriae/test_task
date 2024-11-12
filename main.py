import requests
from bs4 import BeautifulSoup

url = 'https://www.work.ua/resumes-it-python/'
work_request = requests.get(url)

soup = BeautifulSoup(work_request.text, "lxml")

vacancies = soup.find_all("div", class_="card card-hover card-search resume-link card-visited wordwrap")

for vacancy in vacancies:
    title = vacancy.find('h2').text.strip()
    name = vacancy.find('span', 'strong-600').text.strip()
    link = "https://www.work.ua" + vacancy.find('a')['href']
    print(f"Вакансия: {title}")
    print(f"Имя: {name}")
    print(f"Ссылка: {link}\n")
