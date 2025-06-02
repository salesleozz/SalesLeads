import time
import requests
from bs4 import BeautifulSoup
import mysql.connector
from colorama import init, Fore, Style
import random
from fake_useragent import UserAgent
from datetime import datetime

init()  # Initialize colorama

def run_produtos(nome_produto, marketplace, db_market):
    # MySQL database connection settings
    db_host = 'localhost'
    db_username = 'root'
    db_password = ''
    db_name = 'marketplaces'

    # Create a MySQL connection
    cnx = mysql.connector.connect(
        user=db_username,
        password=db_password,
        host=db_host,
        database=db_name
    )

    # Create a cursor object
    cursor = cnx.cursor()

    # Get the current date to append to the table name
    current_date = datetime.now().strftime("%Y%m%d")

    # Generate a dynamic table name
    table_name = f"{nome_produto}_{marketplace}_{current_date}".replace(" ", "_").lower()

    # Create the table with the dynamic name if it doesn't exist
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255),
            link VARCHAR(600),
            preco VARCHAR(255)
        )
    """)

    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
    }

    def run_produtos_mercado_livre(nome_produto):
        url = f"https://lista.mercadolivre.com.br/{nome_produto}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            produtos = soup.find_all('li', class_='ui-search-layout__item')
            for produto in produtos:
                nome_element = produto.find('h2', class_='ui-search-item__title')
                nome = nome_element.text.strip() if nome_element else 'Nome não encontrado'
                link_element = produto.find('a', class_='ui-search-item__group__element')
                link = link_element['href'] if link_element else 'Link não encontrado'
                preco_element = produto.find('span', class_='andes-money-amount__fraction')
                preco = preco_element.text.strip() if preco_element else 'Preço não encontrado'

                cursor.execute(f"""
                    INSERT INTO `{table_name}` (nome, link, preco)
                    VALUES (%s, %s, %s)
                """, (nome, link, preco))
            
            cnx.commit()
            return f"Produtos do Mercado Livre inseridos com sucesso na tabela {table_name}!"
        else:
            return f"Erro ao acessar a página do Mercado Livre: {response.status_code}"

    def run_produtos_amazon(nome_produto):
        url = f"https://www.amazon.com.br/s?k={nome_produto}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            produtos = soup.find_all('div', {'data-component-type': 's-search-result'})
            for produto in produtos:
                nome_element = produto.find('span', class_='a-size-base-plus a-color-base a-text-normal')
                nome = nome_element.text.strip() if nome_element else 'Nome não encontrado'
                link_element = produto.find('a', class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')
                link = f"https://www.amazon.com.br{link_element['href']}" if link_element else 'Link não encontrado'
                preco_element = produto.find('span', class_='a-price-whole')
                preco = preco_element.text.strip() if preco_element else 'Preço não encontrado'

                cursor.execute(f"""
                    INSERT INTO `{table_name}` (nome, link, preco)
                    VALUES (%s, %s, %s)
                """, (nome, link, preco))
            
            cnx.commit()
            return f"Produtos da Amazon inseridos com sucesso na tabela {table_name}!"
        else:
            if response.status_code == 503:
                time.sleep(random.uniform(5, 10))  # Wait for 5-10 seconds before retrying
                return run_produtos_amazon(nome_produto)
            else:
                return f"Erro ao acessar a página da Amazon: {response.status_code}"

    def run_produtos_magalu(nome_produto):
        url = f"https://www.magazineluiza.com.br/busca/{nome_produto}/"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            produtos = soup.find_all('li', class_='sc-CCtys ddCamx')
            for produto in produtos:
                nome_element = produto.find('h2', class_='sc-APcvf eAHIqQ')
                nome = nome_element.text.strip() if nome_element else 'Nome não encontrado'
                link_element = produto.find('a', class_='sc-dCFHLb klIJqU sc-doohEh jwQQUG sc-doohEh jwQQUG')
                link = f"https://www.magazineluiza.com.br{link_element['href']}" if link_element else 'Link não encontrado'
                preco_element = produto.find('p', class_='sc-kpDqfm efxPhd sc-fFlnrN fesnkm')
                preco = preco_element.text.strip() if preco_element else 'Preço não encontrado'

                cursor.execute(f"""
                    INSERT INTO `{table_name}` (nome, link, preco)
                    VALUES (%s, %s, %s)
                """, (nome, link, preco))
            
            cnx.commit()
            return f"Produtos do Magazine Luiza inseridos com sucesso na tabela {table_name}!"
        else:
            if response.status_code == 503:
                time.sleep(random.uniform(5, 10))  # Wait for 5-10 seconds before retrying
                return run_produtos_magalu(nome_produto)
            else:
                return f"Erro ao acessar a página do Magazine Luiza: {response.status_code}"

    # Call the appropriate function based on the marketplace
    if marketplace == 'mercadolivre':
        result = run_produtos_mercado_livre(nome_produto)
    elif marketplace == 'amazon':
        result = run_produtos_amazon(nome_produto)
    elif marketplace == 'magalu':
        result = run_produtos_magalu(nome_produto)
    else:
        result = "Marketplace inválido. Escolha entre 'mercadolivre', 'amazon', ou 'magalu'."

    # Close the cursor and connection
    cursor.close()
    cnx.close()

    return result
