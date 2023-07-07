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
    
def fn_org(num):
    url = os.getenv('url')
    url = f"{url}page/{num}"
    soup = get_soup(url)
    div_tags = soup.find_all('div', class_='tdb_module_loop td_module_wrap td-animation-stack td-cpt-post')
    result_list = []  # Empty list to store the information

    for div in div_tags:
        image_tag = div.find('span', class_='entry-thumb td-thumb-css')
        if image_tag:
            image_url = image_tag['data-img-url']

        h3_tag = div.find('h3', class_='entry-title td-module-title')
        if h3_tag:
            a_tag = h3_tag.find('a')
            if a_tag:
                title = a_tag.text
                link = a_tag['href']
                result_list.append({"title": title, "url": link, "img": image_url})  # Append title, link, and image URL together as a dictionary to the list

    return result_list

def apc():
    url = os.getenv('url2')
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
    info = 'Rating : ' + soup.find('div', class_='summary-content vote-details').text.replace(Title, '').strip() + '\n\nGenres : ' + soup.find('div', class_='genres-content').text.strip()
    chapters = soup.find_all('li', class_='wp-manga-chapter')
    chapter_list = []
    for chapter in chapters:
        a_tag = chapter.find('a')
        if a_tag:
            link = a_tag['href']
            title = a_tag.text.strip()
            chapter_list.append({"title": title, "url": link})
    return Title, image, summary, info, chapter_list