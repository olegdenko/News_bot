import requests
from bs4 import BeautifulSoup

def scrape_news(url):
    # Виконуємо запит на веб-сайт
    response = requests.get(url)
    # Перевіряємо, чи успішно завантажили сторінку
    if response.status_code == 200:
        # Розбираємо HTML з використанням BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        # Знаходимо елементи з новинами на сторінці
        news_elements = soup.find_all('article')
        # Збираємо дані про кожну новину
        news_data = []
        for element in news_elements:
            # Знаходимо заголовок новини
            title_element = element.find('h2').find('a')
            if title_element:
                # Отримуємо текст заголовка
                title = title_element.get_text().strip()
                # Отримуємо посилання на повний текст новини
                link = title_element['href']
                # Зчитуємо повний текст новини
                full_article_url = "https://www.ukrinform.ua" + link
                full_article_response = requests.get(full_article_url)
                if full_article_response.status_code == 200:
                    full_article_soup = BeautifulSoup(full_article_response.text, 'html.parser')
                    article_text_element = full_article_soup.find('div', class_='article__text')
                    if article_text_element:
                        article_text = article_text_element.get_text().strip()
                    else:
                        # Якщо елемент article__text не знайдено, спробуємо знайти інші елементи для тексту новини
                        article_text_element = full_article_soup.find('div', class_='newsHeading')
                        if article_text_element:
                            article_text = article_text_element.get_text().strip()
                        else:
                            # Якщо елемент newsHeading також не знайдено, спробуємо знайти елементи <p>
                            article_text_elements = full_article_soup.find_all('p')
                            if article_text_elements:
                                article_text = "\n".join([p.get_text().strip() for p in article_text_elements])
                            else:
                                article_text = "Повний текст новини відсутній."
                else:
                    article_text = "Не вдалося зчитати повний текст новини."
                # Зберігаємо дані про новину у словнику
                news_item = {
                    'title': title,
                    'link': link,
                    'article_text': article_text
                }
                # Додаємо словник до списку новин
                news_data.append(news_item)
        # Повертаємо список словників із даними про новини
        return news_data
    else:
        print("Не вдалося завантажити сторінку.")
        return []

# Приклад використання функції для скрапінгу новин з сайту
url = "https://www.ukrinform.ua/block-lastnews"
news_data = scrape_news(url)
for news_item in news_data:
    print("Заголовок:", news_item['title'])
    print("Повний текст новини:")
    print(news_item['article_text'])
    print("-" * 50)
