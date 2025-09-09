import asyncio
import datetime

from sqlalchemy import select

from config import VERSION
from db.models import Session, ProductLink
from bot import bot
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome

from markets.parser_ozon import parser_ozon
from markets.parser_wb import parser_wb
from markets.parser_yandex import parser_yandex


async def scheduler():
    while True:
        start_time = datetime.datetime.now()
        try:
            print(1)
            # Настройка опций браузера
            options_uc = uc.ChromeOptions()
            options_uc.add_argument('--headless=new')
            options_uc.add_argument('--disable-blink-features=AutomationControlled')
            options_uc.add_argument('--disable-gpu')
            options_uc.add_argument('--no-sandbox')
            options_uc.add_argument('--disable-setuid-sandbox')
            options_uc.add_argument('--disable-dev-shm-usage')
            options_uc.add_argument('--remote-debugging-port=9222')
            options_uc.add_argument('--disable-extensions')
            options_uc.add_argument('--disable-application-cache')
            options_uc.add_argument('--disable-background-timer-throttling')
            options_uc.add_argument('--disable-backgrounding-occluded-windows')
            options_uc.add_argument('--disable-renderer-backgrounding')
            options_uc.add_argument('--disable-cache')
            options_uc.add_argument('--disable-software-rasterizer')
            options_uc.add_argument('--disable-background-networking')
            options_uc.add_argument('--disable-default-apps')
            options_uc.add_argument('--disable-sync')
            options_uc.add_argument('--disable-translate')
            options_uc.add_argument('--metrics-recording-only')
            options_uc.add_argument('--no-first-run')
            options_uc.add_argument('--safebrowsing-disable-auto-update')
            options_uc.add_argument('--password-store=basic')
            options_uc.add_argument('--autoplay-policy=user-gesture-required')
            options_uc.add_argument('--enable-features=UserAgentClientHint')
            options_uc.add_argument('--window-size=1920,1080')
            options_uc.add_argument(
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Инициализация undetected-chromedriver
            browser_uc = uc.Chrome(options=options_uc, version_main=VERSION)
            browser_uc.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            browser_uc.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print(2)
            chrome_driver_path = ChromeDriverManager().install()
            browser_service = Service(executable_path=chrome_driver_path)
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument("--start-maximized")
            options.page_load_strategy = 'eager'
            options.add_argument('--disable-blink-features=AutomationControlled')
            browser = Chrome(service=browser_service, options=options)
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
            print(3)
            async with Session() as session:
                result = await session.execute(select(ProductLink))
                all_links = result.scalars().all()
                await bot.send_message(1012882762, f'{len(all_links)}')
                browser_uc.get('https://www.wildberries.ru/catalog/173182258/detail.aspx?size=287264697')
                await asyncio.sleep(3)
                for link in all_links:
                    try:
                        if 'wildberries' in link.link_url:
                            new_name, new_price = parser_wb(browser_uc, link.link_url)
                        # elif 'ozon' in link.link_url:
                        #     new_name, new_price = parser_ozon(browser_uc, link.link_url)
                        elif 'market.yandex' in link.link_url:
                            new_name, new_price = parser_yandex(browser, link.link_url)
                        else:
                            try:
                                await bot.send_message(link.user_id,
                                                       f"Ошибка при обработке ссылки {link.link_url}, проверьте ее корректность в браузере.\n"
                                                       f"Если ссылка не корректна, то удалите ее командой /remove")
                            except:
                                pass
                        print(new_name)
                        print(new_price)
                        if not new_price and new_name:
                            await bot.send_message(1012882762, f'{link.link_url} - цена не определилась')

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
                                try:
                                    await bot.send_message(link.user_id, message, disable_web_page_preview=True)
                                except:
                                    pass

                            # Обновляем данные в БД
                            link.name = new_name
                            link.price = new_price
                            await session.commit()

                    except Exception as e:
                        print(e)
                        try:
                            await bot.send_message(link.user_id, f"Ошибка при обработке ссылки {link.link_url}, проверьте ее корректность в браузере.\n"
                                                             f"Если ссылка не корректна, то удалите ее командой /remove")
                        except:
                            pass
                        await session.rollback()
            browser.quit()
            browser_uc.quit()
        except Exception as e:
            await bot.send_message(1012882762, str(e))
        elapsed = datetime.datetime.now() - start_time  # Время выполнения задачи
        wait_time = max(datetime.timedelta(hours=3) - elapsed, datetime.timedelta(0))  # Ждём оставшееся время
        await asyncio.sleep(wait_time.total_seconds())  # Ожидание до следующего цикла

if __name__ == '__main__':
    asyncio.run(scheduler())
