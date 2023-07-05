import requests
from bs4 import BeautifulSoup
import os

url = os.getenv('url')

def get_soup():
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')
    return soup
    
def latest():
    soup = get_soup()
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
