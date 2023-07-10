import requests
from bs4 import BeautifulSoup
import img2pdf
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

    try :
        titles = content.find_all('h3', class_='h5')
    except:
        return []
    photos = content.find_all('img')
    ratings = content.find_all('span', class_='score font-meta total_votes')
    chapters = content.find_all('div', class_='list-chapter')

    results = []

    for title, photo, rating, chapter in zip(titles, photos, ratings, chapters):
        result = {}
        a_tag = title.find('a')
        if a_tag:
            result['title'] = a_tag.text.strip()
            result['link'] = a_tag['href']

        result['img'] = photo['data-src']
        result['rating'] = rating.text.strip()

        first_chapter = chapter.find('div', class_='chapter-item')
        if first_chapter:
            result['chapter'] = first_chapter.find('span', class_='chapter font-meta').text.strip()
            result['chapter_url'] = first_chapter.find('a', class_='btn-link')['href']

        results.append(result)
    return results


def get_comic_images(url):
    soup = get_soup(url)
    content = soup.find('div', class_='reading-content')
    image_tags = content.find_all('img', class_='wp-manga-chapter-img')
    image_links = [img['data-src'].strip() for img in image_tags]
    return image_links

def get_comic_info(url):
    soup = get_soup(url)
    title = soup.find('div', class_='post-title').find('h1').text.strip()
    image_url = soup.find('div', class_='summary_image').find('img')['data-src'].strip()
    summary = soup.find('div', class_='summary__content').find('p').text.strip()
    rating = soup.find('div', class_='summary-content vote-details').text.replace(title, '').strip()
    genres = soup.find('div', class_='genres-content').text.strip()

    chapter_list = []
    chapters = soup.find_all('li', class_='wp-manga-chapter')
    for chapter in chapters:
        a_tag = chapter.find('a')
        if a_tag:
            link = a_tag['href']
            chapter_title = a_tag.text.strip()
            chapter_list.append({"title": chapter_title, "url": link})

    return title, image_url, summary, rating, genres, chapter_list
    
    
def search(query, n):
    url = os.getenv('url') + 'page/' + str(n) + '/?s=' + query + '&post_type=wp-manga&m_orderby=views'
    soup = get_soup(url)

    try:
        results_heading = soup.find('h1', class_='h4').text.strip()
    except:
        return None, None
        
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

def images_to_pdf(links_list, title):
    image_paths = []
    os.makedirs('images', exist_ok=True)
    n = 0
    for i, image_link in enumerate(links_list):
        response = requests.get(image_link, headers=headers)
        if response.status_code == 200:
            image_path = 'images/' + f'image_{i+1}.jpg'
            with open(image_path, 'wb') as image_file:
                image_file.write(response.content)
            image_paths.append(image_path)
        else:
            n+=1
    pdf = f'{title}.pdf'
    with open(pdf, "wb") as f:
        f.write(img2pdf.convert(image_paths))
    return pdf, n
