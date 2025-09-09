import time

import bs4


def parser_ozon(browser, url):
    browser.get(url)
    time.sleep(2)

    html = browser.page_source
    soup = bs4.BeautifulSoup(html, 'lxml')

    # Парсим название товара
    try:
        new_name = soup.find('h1').text.strip()
    except:
        try:
            new_name = soup.find(attrs={"class": "webProductHeading"}).text.strip()
        except:
            new_name = None

    # Парсим цену
    try:
        price_text = soup.find(attrs={"class": "tsHeadline600Large"}).text.strip()
        digits = ''.join([c for c in price_text if c.isdigit()])
        new_price = int(digits) if digits else None
    except:
        new_price = None
    return new_name, new_price
