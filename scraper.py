import string
import os
import os.path

import requests
from urllib.parse import urlencode, urlunsplit

from bs4 import BeautifulSoup


def main():
    input_page_number, input_article_type = int(input()), input()

    for i in range(1, input_page_number + 1):
        articles = get_articles(prep_url(page_number=i), input_article_type)

        if articles:
            for article in articles:
                store_article(article[0], article[1], folder=f'Page_{i}')
        else:
            if not os.access(f'Page_{i}', os.F_OK):
                os.mkdir(f'Page_{i}')


def prep_url(year=2020, page_number=None):
    netloc = 'www.nature.com'
    path = '/nature/articles'

    query = {'sort': 'PubDate', 'year': year}
    if page_number:
        query['page'] = page_number

    return urlunsplit(('https', netloc, path, urlencode(query), ''))


def get_articles(url, article_type='News'):
    rr = requests.get(url)
    rr_html_tree = BeautifulSoup(rr.content, 'html.parser')
    articles = rr_html_tree.find_all('article')

    if articles:
        result = []

        for article in articles:
            category_tag = article.find('span', string=article_type)

            if category_tag:
                content_tag = \
                    category_tag.find_parent('div').find_previous_sibling()

                if content_tag:
                    title = content_tag.h3.get_text().strip()
                    art_rr = requests.get('https://www.nature.com' +
                                          content_tag.h3.a.get('href'))
                    art_rr_html_tree = \
                        BeautifulSoup(art_rr.content, 'html.parser')
                    text = art_rr_html_tree.\
                        find('div', {'class': 'c-article-body'}).\
                        get_text().strip()
                    result.append([title, text])

        if result:
            return result
    return None


def store_article(title, text, folder=None):
    filename = title.translate(
        title.maketrans(' ', '_', string.punctuation)) + '.txt'

    if folder:
        if not os.access(folder, os.F_OK):
            os.mkdir(folder)
            filename = os.path.join(folder, filename)

    with open(filename, 'w', encoding='utf-8') as fh:
        fh.write(text)


if __name__ == '__main__':
    main()
