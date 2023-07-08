import json
import os
import requests
from bs4 import BeautifulSoup


def get_data(url):
    # url = 'https://www.parsemachine.com/sandbox/catalog/' - это тестовый стенд для парсинга

    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15"
    }
    # Создаем директорию, в которой будут храниться данные товаров
    if not os.path.exists('pages_data'):
        os.mkdir('pages_data')
    else:
        pass
    # Цикл для получения нформации со всех страниц сайта (пагинация)
    for page in range(1, 11):
        req = requests.get(url + f'?page={page}', headers=headers)
        src = req.text

        # Закоменченный блок, если сохранять ответ запроса в файл и парсить содержимое файла
        # with open('catalogs_response.html', 'w') as file:
        #     file.write(req.text)

        # with open('catalogs_response.html') as file:
        #     src = file.read()

        soup = BeautifulSoup(src, 'lxml')
        product_cards = soup.find_all(class_='no-hover title')
        # Достаем endpoint всех товаров для получения url всех товаров
        url_product_cards = []
        for tovar in product_cards:
            tovar_endpoint = tovar.get('href')
            url_product_cards.append('https://www.parsemachine.com' + tovar_endpoint)

        product_data = []
        # Получаем словарь со всей нужной информацией по товарам
        for url_product_card in url_product_cards:

            req = requests.get(url_product_card, headers)
            soup = BeautifulSoup(req.text, 'lxml')
            try:
                product_name = soup.find(id='product_name').text.strip()
            except Exception:
                product_name = 'Имя товара не обнаружено'
            try:
                product_price = soup.find(id="product_amount").text.strip() + ' руб.'
            except Exception:
                product_price = 'Цена товара не обнаружена'
            try:
                product_all_characteristics = soup.find(id='characteristics')
                width = product_all_characteristics.find('tr').find_next('td').find_next().text
                hight = product_all_characteristics.find('tr').find_next('tr').find('td').find_next().text
                depth = product_all_characteristics.find('tr').find_next('tr').find_next('tr').find(
                    'td').find_next().text
                product_characteristics = {
                    'Ширина': f'{width}',
                    'Высота': f'{hight}',
                    'Глубина': f'{depth}'
                }
            except Exception:
                product_characteristics = 'Нет характеристик'
            try:
                product_article = soup.find(id='sku').text
            except Exception:
                product_article = 'Артикул не найден'
            try:
                product_description = ' '.join(soup.find(id='description').text.split())
            except Exception:
                product_description = 'Описание не найдено'
            product_data.append(
                {
                    "Наименование товара": product_name,
                    "Артикул товара": product_article,
                    "Цена": product_price,
                    "Характеристики товара": product_characteristics,
                    "Описание товара": product_description
                }
            )

        if not os.path.exists(f'./pages_data/{page}'):
            os.mkdir(f'./pages_data/{page}')
            with open(f'./pages_data/{page}/products_data.json', 'a', encoding='utf-8') as file:
                json.dump(product_data, file, indent=4, ensure_ascii=False)
        else:
            with open(f'./pages_data/{page}/products_data.json', 'a', encoding='utf-8') as file:
                json.dump(product_data, file, indent=4, ensure_ascii=False)


get_data('https://www.parsemachine.com/sandbox/catalog/')
