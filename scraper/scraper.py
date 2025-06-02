from playwright.sync_api import sync_playwright
from dataclasses import dataclass, field
import mysql.connector
from datetime import datetime

@dataclass
class Business:
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None

@dataclass
class BusinessList:
    business_list: list[Business] = field(default_factory=list)

    def save_to_db(self, db_config, pesquisa):
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        table_name = f"{pesquisa}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255),
                endereco VARCHAR(255),
                website VARCHAR(255),
                numero_telefone VARCHAR(50)
            )
        ''')

        for business in self.business_list:
            cursor.execute(f'''
                INSERT INTO {table_name} (nome, endereco, website, numero_telefone)
                VALUES (%s, %s, %s, %s)
            ''', (business.name, business.address, business.website, business.phone_number))

        connection.commit()
        cursor.close()
        connection.close()

def run_scraper(pesquisa, db_config):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto('https://www.google.com/maps', timeout=60000)
        page.wait_for_timeout(6000)

        page.locator('//input[@id="searchboxinput"]').fill(pesquisa)
        page.wait_for_timeout(5000)

        page.keyboard.press('Enter')
        page.wait_for_timeout(3000)

        if pesquisa.lower() in ['veterinários', 'advogados','hospitais','eletricistas','faculdades','mecânicas','creches','farmácias','imobiliárias','gráficas','empreiteiro','seguros','escolas']:
            listing_xpath = '//div[@class="Nv2PK tH5CWc THOPZb "]'
        else:
            listing_xpath = '//div[@class="Nv2PK THOPZb CpccDe "]'

        page.hover(f'({listing_xpath})[1]')
        
        previous_count = 0
        while True:
            page.mouse.wheel(0, 10000)
            page.wait_for_timeout(8000)

            current_count = page.locator(listing_xpath).count()
            if current_count == previous_count:
                print(f'Total Scraped: {current_count}')
                break
            else:
                previous_count = current_count
                print(f'Currently Scraped: {current_count}')

        listings = page.locator(listing_xpath).all()

        business_list = BusinessList()

        for index, listing in enumerate(listings):
            try:
                listing.scroll_into_view_if_needed()
                page.wait_for_selector(f"({listing_xpath})[{index + 1}]", state="visible", timeout=60000)
                listing.click(timeout=60000)
                page.wait_for_timeout(5000)

                name_xpath = '//h1[contains(@class, "DUwDvf lfPIob")]'
                address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "Io6YTe fontBodyMedium kR99db ")]'
                website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "Io6YTe fontBodyMedium kR99db ")]'
                phone_number_xpath = '//button[contains(@class, "CsEnBe")]//div[@class="Io6YTe fontBodyMedium kR99db " and starts-with(text(), "(")]'

                business = Business()
                
                business.name = page.locator(name_xpath).inner_text() if page.locator(name_xpath).count() > 0 else "Nome Indisponível"
                business.address = page.locator(address_xpath).inner_text() if page.locator(address_xpath).count() > 0 else "Endereço Indisponível"
                business.website = page.locator(website_xpath).inner_text() if page.locator(website_xpath).count() > 0 else "Website Indisponível"
                business.phone_number = page.locator(phone_number_xpath).inner_text() if page.locator(phone_number_xpath).count() > 0 else "Número de Telefone Indisponível"
                
                business_list.business_list.append(business)
            
            except Exception as e:
                print(f"Error clicking on listing {index}: {e}")

        business_list.save_to_db(db_config, pesquisa)

        browser.close()
