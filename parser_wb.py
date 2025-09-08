import asyncio

import bs4
from sqlalchemy import select

from db.models import Session, ProductLink
from bot import bot

from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome


async def scheduler():
    while True:
        try:
            chrome_driver_path: str = ChromeDriverManager().install()
            browser_service: Service = Service(executable_path=chrome_driver_path)

            # Настройка опций браузера
            options: Options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.page_load_strategy = 'eager'
            options.add_argument('--blink-settings=imagesEnabled=false')
            options.add_argument('--disable-blink-features=AutomationControlled')

            browser: Chrome = Chrome(service=browser_service, options=options)

            # Обход анти-бот защиты
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
            async with Session() as session:
                result = await session.execute(select(ProductLink))
                all_links = result.scalars().all()

                for link in all_links:
                    try:
                        browser.get(link.link_url)
                        await asyncio.sleep(3)
                        html = browser.page_source
                        soup = bs4.BeautifulSoup(html, 'lxml')

                        # Парсим название товара
                        try:
                            new_name = soup.find('h1').text.strip()
                        except:
                            new_name = None

                        # Парсим цену
                        try:
                            price_text = soup.find(attrs={"class": "priceBlockWalletPrice--RJGuT"}).text.strip()
                            digits = ''.join([c for c in price_text if c.isdigit()])
                            new_price = int(digits) if digits else None
                        except:
                            new_price = None
                        print(new_name)
                        print(new_price)

                        # Если данные получены успешно
                        if new_name and new_price:
                            # Проверяем изменение цены
                            if link.price and new_price < link.price:
                                message = (
                                    f"💰 Цена уменьшилась!\n"
                                    f"📦 Товар: {new_name}\n"
                                    f"🔗 Ссылка: {link.link_url}\n"
                                    f"📉 Старая цена: {link.price} руб.\n"
                                    f"📈 Новая цена: {new_price} руб."
                                )
                                await bot.send_message(link.user_id, message)

                            # Обновляем данные в БД
                            link.name = new_name
                            link.price = new_price
                            await session.commit()

                    except:
                        await bot.send_message(link.user_id, f"Ошибка при обработке ссылки {link.link_url}, проверьте ее корректность в браузере.\n"
                                                             f"Если ссылка не корректна, то удалите ее командой /remove")
                        await session.rollback()
            browser.quit()
        except Exception as e:
            await bot.send_message(1012882762, str(e))
        await asyncio.sleep(8000)

if __name__ == '__main__':
    asyncio.run(scheduler())
