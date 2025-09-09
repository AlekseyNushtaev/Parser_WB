import time

import bs4
import asyncio
import datetime

from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy import select

from config import VERSION
from db.models import Session, ProductLink
from bot import bot
import undetected_chromedriver as uc

from markets.parser_wb import parser_wb
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


print(1)
# Настройка опций браузера
options_uc = uc.ChromeOptions()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
options_uc.add_argument('--disable-dev-shm-usage')
options_uc.add_argument('--disable-blink-features=AutomationControlled')
options_uc.add_argument('--disable-gpu')
options_uc.add_argument('--disable-extensions')
options_uc.add_argument('--disable-popup-blocking')
options_uc.add_argument('--disable-features=VizDisplayCompositor')
options_uc.add_argument('--disable-accelerated-2d-canvas')
options_uc.add_argument('--disable-webgl')
options_uc.add_argument('--no-first-run')
options_uc.add_argument('--no-zygote')
options_uc.add_argument('--single-process')
options_uc.add_argument('--disable-setuid-sandbox')
options_uc.add_argument('--disable-blink-features=AutomationControlled')

# Установка пользовательского User-Agent
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
options_uc.add_argument(f'--user-agent={user_agent}')
print(2)
# Инициализация undetected-chromedriver
browser_uc = uc.Chrome(options=options_uc, version_main=VERSION)
browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    'source': '''
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
    '''
    })
url = 'https://www.ozon.ru/product/oppo-smartfon-a5x-rostest-eac-4-128-gb-siniy-2189766691/?at=EqtkVN2ZVho5wqAycR7N0nDH7Jl68AfjgoQqyC5DA4k9'
browser.get(url)
WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
time.sleep(20)

html = browser.page_source
soup = bs4.BeautifulSoup(html, 'lxml')

# Парсим название товара
try:
    new_name = soup.find('h1').text.strip()
except:
    try:
        new_name = soup.find(attrs={"class": "pdp_b6f tsHeadline550Medium"}).text.strip()
    except:
        new_name = None
print(new_name)
# Парсим цену
try:
    price_text = soup.find(attrs={"class": "tsHeadline600Large"}).text.strip()
    digits = ''.join([c for c in price_text if c.isdigit()])
    new_price = int(digits) if digits else None
except:
    try:
        price_text = soup.find(attrs={"class": "tsHeadline600Large"}).text.strip()
        digits = ''.join([c for c in price_text if c.isdigit()])
        new_price = int(digits) if digits else None
    except:
        try:
            price_text = soup.find(
                attrs={"class": "tsHeadline600Large"}).text.strip()
            digits = ''.join([c for c in price_text if c.isdigit()])
            new_price = int(digits) if digits else None
        except:
            new_price = None
print(new_price)
browser.quit()
