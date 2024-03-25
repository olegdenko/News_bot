import requests
from bs4 import BeautifulSoup

import spacy
# from spacy.lang.uk.examples import sentences
from heapq import nlargest

# URL веб-сайту для скрапінгу новин
URL = "https://www.ukrinform.ua/block-lastnews"

# Завантаження мовної моделі SpaCy
nlp = spacy.load('uk_core_news_sm')


# Функція для отримання тексту новин з веб-сайту
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

def summarize(text, num_sentences):
    # Токенізація речень за допомогою SpaCy
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]

    # Видалення зайвих символів та обробка тексту
    tokens = [token.text.lower() for token in doc if not token.is_stop and token.is_alpha]
    words = ' '.join(tokens)

    # Обробка речень
    sentence_tokens = [nlp(sent) for sent in sentences]
    word_frequencies = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() not in tokens:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1

    # Визначення важливості речень
    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word] / max_frequency)

    # Сортування та вибір найважливіших речень
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text in word_frequencies.keys():
                if sent.text not in sentence_scores.keys():
                    sentence_scores[sent.text] = word_frequencies[word.text]
                else:
                    sentence_scores[sent.text] += word_frequencies[word.text]

    select_length = min(num_sentences, len(sentences))
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)
    return ' '.join(summary)


# Отримання текстів новин
news_data = scrape_news(URL)

# Кількість речень у summary
num_sentences_summary = 5

# Отримання текстового резюме
if news_data:
    news = ""
    for news_item in news_data:
        news += news_item['title'] + " " + news_item['article_text'] + "\n"
    print("Combined news text: ", news)
    summary = summarize(news, num_sentences_summary)
    print("Summary: ", summary)
else:
    print("Немає новин для обробки.")
