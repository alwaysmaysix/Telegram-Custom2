import requests
from bs4 import BeautifulSoup
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}
def get_soup(url):
    response = requests.get(url, headers=headers)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup

def apc():
    url = os.getenv('url') + 'home-3/'
    soup = get_soup(url)
    content = soup.find('div', class_='page-content-listing item-big_thumbnail')

    titles = content.find_all('h3', class_="h5")
    photos = content.find_all('img')
    ratings = content.find_all('span', class_="score font-meta total_votes")
    chapters = content.find_all('div', class_="list-chapter")
    results = []

    for title, photo, rating, chapter in zip(titles, photos, ratings, chapters):
        title_dict = {}
        a_tag = title.find('a')
        if a_tag:
            title_text = a_tag.text.strip()
            link = a_tag['href']
            title_dict['title'] = title_text
            title_dict['link'] = link

        img = photo['data-src']
        title_dict['img'] = img

        rating_text = rating.text.strip()
        title_dict['rating'] = rating_text
        
        first_chapter = chapter.find('div', class_='chapter-item')
        if first_chapter:
            chapter_title = first_chapter.find('span', class_='chapter font-meta').text.strip()
            chapter_url = first_chapter.find('a', class_='btn-link')['href']
            title_dict['chapter'] = chapter_title
            title_dict['chapter_url'] = chapter_url
        
        results.append(title_dict)

    return results


def get_comic(url):
    soup = get_soup(url)
    content = soup.find('div', class_='reading-content')
    image_tags = content.find_all('img', class_='wp-manga-chapter-img')
    links = [img['data-src'].strip() for img in image_tags]
    return links
    
def get_comic_info(url):
    soup = get_soup(url)
    Title = soup.find('div', class_='post-title').find('h1').text.strip()
    image = soup.find('div', class_='summary_image').find('img')['data-src'].strip()
    summary = soup.find('div', class_='summary__content').find('p').text.strip()
    info = '⭐Rating \n' + soup.find('div', class_='summary-content vote-details').text.replace(Title, '').strip() + '\n\n🛑Genres\n' + soup.find('div', class_='genres-content').text.strip()
    chapters = soup.find_all('li', class_='wp-manga-chapter')
    chapter_list = []
    for chapter in chapters:
        a_tag = chapter.find('a')
        if a_tag:
            link = a_tag['href']
            title = a_tag.text.strip()
            chapter_list.append({"title": title, "url": link})
    return Title, image, summary, info, chapter_list
    
    
def search(query):
    url = os.getenv('url') + 'page/1/?s=' + query + '&post_type=wp-manga&m_orderby=views'
    soup = get_soup(url)
    results_heading = soup.find('h1', class_='h4').text.strip()

    images = soup.find_all('div', class_='tab-thumb c-image-hover')
    titles = soup.find_all('div', class_='post-title')
    summaries = soup.find_all('div', class_='post-content')
    latest_chapters = soup.find_all('div', class_='meta-item latest-chap')
    ratings = soup.find_all('span', class_='score font-meta total_votes')

    results = []

    for image, title, summary, chapter, rating in zip(images, titles, summaries, latest_chapters, ratings):
        item_dict = {}

        a_tag = title.find('a')
        item_dict['title'] = a_tag.text.strip()
        item_dict['url'] = a_tag['href']

        img_url = image.find('img')['data-src']
        item_dict['image'] = img_url

        data = summary.find_all('div', class_='summary-content')
        item_dict['status'] = data[2].text.strip()
        item_dict['genres'] = data[1].text.strip()

        chapter_link = chapter.find('a')['href']
        item_dict['chapter'] = chapter.find('a').text.strip()
        item_dict['chapter_url'] = chapter_link
        
        item_dict['rating'] = rating.text.strip()

        results.append(item_dict)

    return results_heading, results
