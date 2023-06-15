import requests
from fake_headers import Headers
from bs4 import BeautifulSoup
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
import json
import time


HOST = "https://spb.hh.ru"
href = r"/search/vacancy?text=python+Django+Flask&area=1&area=2&page="

def get_headers():
    return Headers(browser="chrome", os="win").generate()

def get_text(url):
    return requests.get(url, headers=get_headers()).text

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    service = Service(eexecutable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return(driver)

def number_of_pages(soup):
    numbers = soup.find_all("a", attrs={"class":"bloko-button", "data-qa":"pager-page"})
    list_nuber = []
    for number in numbers:
        list_nuber.append(int(number.text))
    number_of_pages = max(list_nuber)
    return (number_of_pages)

def get_links():
    links = []
    driver = get_driver()
    driver.get(url=f"{HOST}{href}{0}")
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "lxml")
    for n in tqdm(range(number_of_pages(soup))):
        driver.get(url=f"{HOST}{href}{n}")
        soup = BeautifulSoup(driver.page_source, "lxml")
        items = soup.find_all("a", attrs={"class":"serp-item__title"})
        for item in items:
            links.append(item.get("href"))
    driver.quit()
    return(links)

def info():
    dict_vacancy = {}
    for l in get_links():
        html = get_text(l)
        soup = BeautifulSoup(html, "lxml")
        name = soup.title.string
        salary = soup.find("span", attrs = {"data-qa":"vacancy-salary-compensation-type-net"})
        company = soup.find("span", attrs = {"data-qa":"bloko-header-2", "class":"bloko-header-section-2 bloko-header-section-2_lite"}).text
        city = soup.find("span", attrs = {"data-qa":"vacancy-view-raw-address"})
        link = l
        if city is not None:
            city = city.text
        else:
            city = "Город не указан"

        if salary is not None:
            salary = salary.text
        else:
            salary = "ЗП не указана"
        dict_vacancy.update({name:{"Ссылка":link,
                                   "вилка зп":salary,
                                   "название компании":company,
                                   "город":city}})
    return (dict_vacancy)

def create_json(dict_vacancy):
    with open("INFO.json", "w", encoding='utf-8') as json_file:
        json.dump(dict_vacancy, json_file, ensure_ascii=False)


if __name__ == "__main__":
    dict_vacancy = info()
    create_json(dict_vacancy)

