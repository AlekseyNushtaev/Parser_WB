import asyncio
import bs4
from sqlalchemy import select
from db.models import Session, ProductLink
from bot import bot
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options


async def scheduler():
    while True:
        try:
            print(1)
            # Настройка опций браузера
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-accelerated-2d-canvas')
            options.add_argument('--disable-webgl')
            options.add_argument('--no-first-run')
            options.add_argument('--no-zygote')
            options.add_argument('--single-process')
            options.add_argument('--disable-setuid-sandbox')

            # Установка пользовательского User-Agent
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            options.add_argument(f'--user-agent={user_agent}')
            print(2)
            # Инициализация undetected-chromedriver
            browser = uc.Chrome(options=options)
            print(3)
            async with Session() as session:
                result = await session.execute(select(ProductLink))
                all_links = result.scalars().all()

                for link in all_links:
                    try:
                        browser.get(link.link_url)
                        await asyncio.sleep(3)

                        html = browser.page_source
                        soup = bs4.BeautifulSoup(html, 'lxml')
                        souptext = soup.find(attrs={"class": "product-page productPage--KE6FH"})

                        print(souptext.prettify())

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
